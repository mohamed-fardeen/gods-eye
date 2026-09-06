"""
backend/app/ai/anpr_pipeline.py
===============================
God's Eye — ANPR + Tracking Pipeline (Phase 2, branch: tracking_ocr)

Architecture:
  - One capture THREAD feeds BGR frames into a bounded queue (backpressure).
  - Main processing loop runs YOLO vehicle detection + ByteTrack in-order
    (must stay single-threaded for track-ID continuity).
  - OCR is dispatched to a ThreadPoolExecutor — PaddleOCR / YOLO release the
    GIL during their C++/CUDA compute, so real wall-clock overlap happens.
  - Per-track voting: each TrackState accumulates plate readings + confidence
    scores. Once CONFIDENT_VOTE_COUNT votes converge, OCR stops for that track
    (early-exit / ROI caching).
  - Confidence-native: every stage emits a probability. Combined score =
    plate_det_conf × ocr_conf. Alerts carry the compound trust score.
  - Fuzzy watchlist matching via RapidFuzz (Levenshtein) so OCR-misread plates
    still trigger alerts.

Reference: Untitled1.ipynb (Colab v2 notebook) + deep-research-report.md

Usage (standalone test):
    python -m app.ai.anpr_pipeline --source 0          # webcam
    python -m app.ai.anpr_pipeline --source video.mp4  # file
"""

from __future__ import annotations

import logging
import os
import queue
import re
import threading
import time
import math
import queue
from collections import Counter, defaultdict
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

# ── Fix PaddleOCR oneDNN/MKLDNN crash BEFORE any paddle import ────────────────
# This env-var must be set before importing paddleocr. It disables Intel's
# oneDNN back-end that causes a known crash on many Windows/Linux setups.
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "0")
os.environ.setdefault("FLAGS_use_mkldnn", "0")

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline configuration (tune these at the top — they're referenced throughout)
# ─────────────────────────────────────────────────────────────────────────────

# YOLO vehicle classes from COCO: car=2, motorcycle=3, bus=5, truck=7
VEHICLE_CLASS_IDS: List[int] = [2, 3, 5, 7]

# How many frames to wait between OCR attempts per track, BEFORE it is resolved.
# After CONFIDENT_VOTE_COUNT votes converge, OCR stops entirely (early exit).
OCR_SAMPLE_INTERVAL: int = 5

# Process YOLO only every N frames. ByteTrack will interpolate in-between.
SKIP_FRAMES: int = 3

# Discard any OCR result below this combined confidence BEFORE adding to votes.
# Prevents junk reads (distant/blurry/misdetected signs) from polluting voting.
MIN_ACCEPT_CONFIDENCE: float = 0.30

# Once a track's top plate reaches this many votes → mark as resolved, stop OCR.
CONFIDENT_VOTE_COUNT: int = 3

# High confidence threshold for aggressive early-exit
EARLY_EXIT_CONFIDENCE: float = 0.90

# Abandon OCR on a track if we get this many garbage/unreadable results
UNREADABLE_STRIKES_LIMIT: int = 5

# Pre-OCR heuristic filters on the plate bounding box (pixels).
# Indian plates are roughly 2:1 to 5:1 width:height.
MIN_PLATE_AREA_PX: int = 500        # ~25×20 px floor
MIN_PLATE_ASPECT: float = 1.5
MAX_PLATE_ASPECT: float = 6.0

# Loose Indian plate grammar — used as a SOFT weight bonus during voting,
# NOT as a hard filter (real-world crops/fonts vary too much).
INDIAN_PLATE_REGEX = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{3,4}$")

# Background OCR thread pool size. PaddleOCR releases the GIL during inference,
# so real threads provide genuine wall-clock overlap (not just queuing).
OCR_WORKER_THREADS: int = 4

# Bounded capture queue — gives natural backpressure for live camera/RTSP:
# if processing falls behind, capture blocks on put() instead of OOM-ing.
FRAME_QUEUE_MAXSIZE: int = 8

# Minimum fuzzy-match score (0–100) against the watchlist to trigger an alert.
FUZZY_MATCH_THRESHOLD: int = 85

# Common Indian-plate OCR confusions (architecture doc §3.1 / tech stack table).
# Applied when normalizing a candidate plate for watchlist comparison.
CONFUSION_MAP = str.maketrans({
    "O": "0", "I": "1", "B": "8", "S": "5", "Z": "2",
})


# ─────────────────────────────────────────────────────────────────────────────
# Lazy model loader — models are heavy; only load when the pipeline is started.
# This keeps FastAPI startup fast when the ANPR pipeline isn't running yet.
# ─────────────────────────────────────────────────────────────────────────────

_models_loaded = False
_vehicle_model = None
_plate_model = None
_ocr = None
_DEVICE: Any = "cpu"


def _load_models(
    vehicle_model_path: str = "yolov8n.pt",
    plate_model_repo: str = "Koushim/yolov8-license-plate-detection",
    plate_model_file: str = "best.pt",
) -> None:
    """
    Load YOLO (vehicle + plate) and PaddleOCR models once.
    Calling this multiple times is safe (idempotent).
    """
    global _models_loaded, _vehicle_model, _plate_model, _ocr, _DEVICE

    if _models_loaded:
        return

    # ── Detect compute device ─────────────────────────────────────────────────
    try:
        import torch
        _DEVICE = 0 if torch.cuda.is_available() else "cpu"
    except ImportError:
        _DEVICE = "cpu"
    logger.info("ANPR pipeline: using device %s", _DEVICE)

    # ── Vehicle detector (COCO pretrained — no training needed) ──────────────
    if vehicle_model_path is not None:
        from ultralytics import YOLO
        from app.ai.export_model import ensure_yolo_onnx
        
        # Automatically export to ONNX for speed
        if vehicle_model_path.endswith(".pt"):
            vehicle_model_path = ensure_yolo_onnx(vehicle_model_path)
            
        _vehicle_model = YOLO(vehicle_model_path, task='detect')
        logger.info("Vehicle model loaded: %s", vehicle_model_path)

    # ── Plate detector (HuggingFace fine-tuned weights) ───────────────────────
    plate_path = Path(plate_model_file)
    if not plate_path.exists():
        try:
            from huggingface_hub import hf_hub_download
            plate_model_file = hf_hub_download(
                repo_id=plate_model_repo, filename="best.pt"
            )
            logger.info("Plate model downloaded from HF: %s", plate_model_file)
        except Exception as exc:
            logger.warning(
                "Could not download plate model from HF (%s). "
                "Plate detection will be skipped. Error: %s",
                plate_model_repo, exc,
            )
            plate_model_file = None

    if plate_model_file:
        _plate_model = YOLO(plate_model_file)
        logger.info("Plate model loaded: %s", plate_model_file)

    # ── PaddleOCR ─────────────────────────────────────────────────────────────
    _ocr_kwargs = dict(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    try:
        from paddleocr import PaddleOCR
        try:
            _ocr = PaddleOCR(
                device="gpu:0" if _DEVICE == 0 else "cpu", **_ocr_kwargs
            )
            logger.info("PaddleOCR loaded (device: %s)", "gpu:0" if _DEVICE == 0 else "cpu")
        except TypeError:
            # Some PaddleOCR versions don't accept `device=`
            _ocr = PaddleOCR(**_ocr_kwargs)
            logger.info("PaddleOCR loaded (default device — check version for GPU kwarg)")
    except ImportError:
        logger.warning(
            "PaddleOCR not installed. OCR will be unavailable. "
            "Install with: pip install paddleocr paddlepaddle"
        )
        _ocr = None

    _models_loaded = True

def _init_worker(plate_repo: str, plate_file: str) -> None:
    """Initializer for ProcessPoolExecutor workers to load OCR models locally."""
    _load_models(vehicle_model_path=None, plate_model_repo=plate_repo, plate_model_file=plate_file)

# ─────────────────────────────────────────────────────────────────────────────
# OCR helpers
# ─────────────────────────────────────────────────────────────────────────────

def _clean_plate_text(text: str) -> str:
    """Strip everything except uppercase letters and digits."""
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


def _read_plate_with_confidence(crop: np.ndarray) -> Tuple[str, float]:
    """
    Preprocess a plate crop and run PaddleOCR on it.

    Preprocessing pipeline (in order):
      1. Upscale if plate is tiny (<120 px tall) — gives OCR more pixels.
      2. Grayscale → bilateral filter (denoise edges) → CLAHE (local contrast).
      3. Convert grayscale back to BGR — PaddleOCR requires shape (H, W, 3).
         Without this step it crashes with "not enough values to unpack".

    Returns (cleaned_text, confidence). Returns ("UNKNOWN", 0.0) on failure.
    """
    if _ocr is None:
        return "UNKNOWN", 0.0
    if crop is None or crop.size == 0:
        return "UNKNOWN", 0.0

    try:
        h, w = crop.shape[:2]

        # 1. Upscale small plates
        scale = max(1, int(np.ceil(120 / max(h, 1))))
        if scale > 1:
            crop = cv2.resize(crop, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        # 2. Enhance contrast
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 7, 50, 50)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # 3. Back to 3-channel for PaddleOCR
        ocr_input = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        results = _ocr.predict(ocr_input)

        texts: List[str] = []
        scores: List[float] = []

        for result in results:
            # Handle both dict results and PaddleOCR result objects
            data: dict = {}
            if isinstance(result, dict):
                data = result
            elif hasattr(result, "json"):
                try:
                    json_data = result.json
                    data = json_data() if callable(json_data) else json_data
                except Exception:
                    data = {}

            if isinstance(data, dict):
                res = data.get("res", data)
                if isinstance(res, dict):
                    rec_texts = res.get("rec_texts", [])
                    rec_scores = res.get("rec_scores", [])

                    # Multi-line plate support: sort lines top-to-bottom by
                    # vertical centroid so the same plate reads consistently
                    # across frames (avoids vote-splitting between e.g.
                    # "HR97A9533" and "97A9533HR").
                    rec_polys = res.get("rec_polys") or res.get("dt_polys") or []
                    if rec_polys and len(rec_polys) == len(rec_texts):
                        def _line_y(poly: Any) -> float:
                            pts = np.array(poly)
                            return float(pts[:, 1].mean())
                        order = sorted(range(len(rec_texts)), key=lambda i: _line_y(rec_polys[i]))
                        rec_texts = [rec_texts[i] for i in order]
                        rec_scores = [rec_scores[i] for i in order]

                    for t, s in zip(rec_texts, rec_scores):
                        t = str(t).strip()
                        if t:
                            texts.append(t)
                            scores.append(float(s))

        text = _clean_plate_text("".join(texts))
        confidence = max(scores) if scores else 0.0
        return (text if text else "UNKNOWN"), confidence

    except Exception as exc:
        logger.debug("OCR warning (%s): %s", type(exc).__name__, exc)
        return "UNKNOWN", 0.0


def get_plate_reading(
    vehicle_crop: np.ndarray,
    track_id: Optional[int] = None,
) -> Tuple[Optional[str], float]:
    """
    Full plate reading pipeline for a single vehicle crop:
      1. Plate detection (YOLO) on the vehicle crop.
      2. Pre-OCR heuristics: reject junk boxes (tiny area, bad aspect ratio).
      3. PaddleOCR on the best plate crop.
      4. Combined confidence = plate_det_conf × ocr_conf.

    Returns (plate_text, combined_confidence), or (None, 0.0) if no plate found.
    This is called from background OCR worker threads.
    """
    if _plate_model is None:
        return None, 0.0
    if vehicle_crop is None or vehicle_crop.size == 0:
        return None, 0.0

    try:
        plate_results = _plate_model.predict(
            vehicle_crop, conf=0.20, device=_DEVICE, verbose=False
        )[0]
        boxes = plate_results.boxes
        if boxes is None or len(boxes) == 0:
            return None, 0.0

        best_idx = int(boxes.conf.argmax().cpu().item())
        x1, y1, x2, y2 = boxes.xyxy[best_idx].cpu().numpy().astype(int)
        plate_det_conf = float(boxes.conf[best_idx].cpu().item())

        h, w = vehicle_crop.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        box_w, box_h = (x2 - x1), (y2 - y1)
        if box_w <= 0 or box_h <= 0 or box_w * box_h < MIN_PLATE_AREA_PX:
            return None, 0.0
        aspect = box_w / box_h
        if not (MIN_PLATE_ASPECT <= aspect <= MAX_PLATE_ASPECT):
            return None, 0.0

        plate_crop = vehicle_crop[y1:y2, x1:x2]
        text, ocr_conf = _read_plate_with_confidence(plate_crop)
        if text == "UNKNOWN" or not text:
            return None, 0.0

        combined_conf = plate_det_conf * ocr_conf
        return text, combined_conf

    except Exception as exc:
        logger.debug("get_plate_reading error (track %s): %s", track_id, exc)
        return None, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Per-track state — accumulates OCR readings and resolves the best plate
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TrackState:
    """
    Maintains all OCR evidence for a single ByteTrack track ID.

    Design:
    - plate_votes: Counter of how many times each plate string was read.
    - plate_confidences: maps plate → list of per-read confidence scores.
    - Scoring = avg_confidence × vote_count × grammar_bonus (soft, not hard).
    - Once is_confidently_resolved() → True, no more OCR is dispatched for
      this track (early-exit / ROI caching — prevents re-OCRing parked cars).
    """
    plate_votes: Counter = field(default_factory=Counter)
    plate_confidences: Dict[str, List[float]] = field(default_factory=dict)
    frames_seen: int = 0
    alerted: bool = False
    ocr_locked: bool = False
    unreadable_strikes: int = 0

    def add_reading(self, plate: str, conf: float) -> None:
        if plate:
            self.plate_votes[plate] += 1
            self.plate_confidences.setdefault(plate, []).append(conf)

    def resolved_plate(self) -> Tuple[Optional[str], float]:
        """
        Majority vote across all OCR reads, weighted by confidence + grammar.
        Returns (best_plate, avg_confidence) or (None, 0.0) if no reads yet.
        """
        if not self.plate_votes:
            return None, 0.0

        def _score(p: str) -> float:
            confs = self.plate_confidences[p]
            avg_conf = sum(confs) / len(confs)
            grammar_bonus = 1.15 if INDIAN_PLATE_REGEX.match(p) else 1.0
            return avg_conf * self.plate_votes[p] * grammar_bonus

        best = max(self.plate_votes, key=_score)
        confs = self.plate_confidences[best]
        return best, sum(confs) / len(confs)

    def is_confidently_resolved(self) -> bool:
        """True once the top plate has ≥ CONFIDENT_VOTE_COUNT consistent votes, or early exit locked."""
        if self.ocr_locked:
            return True
        if not self.plate_votes:
            return False
        _, top_count = self.plate_votes.most_common(1)[0]
        return top_count >= CONFIDENT_VOTE_COUNT


# ─────────────────────────────────────────────────────────────────────────────
# Watchlist — fuzzy blacklist matching
# ─────────────────────────────────────────────────────────────────────────────

class Watchlist:
    """
    Thread-safe store of blacklisted plates.
    Normalizes plates with CONFUSION_MAP before comparing, so OCR confusions
    (O↔0, I↔1, B↔8, S↔5, Z↔2) don't cause false negatives on blacklisted plates.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, Dict[str, str]] = {}  # normalized → {raw, reason}
        self._lock = threading.Lock()

    def _normalize(self, plate: str) -> str:
        return plate.upper().replace(" ", "").translate(CONFUSION_MAP)

    def add(self, plate: str, reason: str = "flagged") -> None:
        norm = self._normalize(plate)
        with self._lock:
            self._entries[norm] = {"raw": plate.upper(), "reason": reason}
        logger.info("Watchlist: added %s (%s)", plate.upper(), reason)

    def remove(self, plate: str) -> bool:
        norm = self._normalize(plate)
        with self._lock:
            removed = self._entries.pop(norm, None)
        return removed is not None

    def list_all(self) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._entries.values())

    def check(self, candidate: str) -> Tuple[Optional[Dict[str, str]], float]:
        """
        Returns (matched_entry, score) if best fuzzy match ≥ FUZZY_MATCH_THRESHOLD,
        else (None, best_score).
        """
        from rapidfuzz import fuzz
        norm = self._normalize(candidate)
        best_score, best_entry = 0.0, None
        with self._lock:
            entries = list(self._entries.items())
        for norm_plate, entry in entries:
            score = fuzz.ratio(norm, norm_plate)
            if score > best_score:
                best_score, best_entry = score, entry
        if best_score >= FUZZY_MATCH_THRESHOLD:
            return best_entry, best_score
        return None, best_score


# ─────────────────────────────────────────────────────────────────────────────
# Capture thread — the streaming boundary
# ─────────────────────────────────────────────────────────────────────────────

def _capture_thread_fn(
    source: Any,
    frame_queue: "queue.Queue[Optional[np.ndarray]]",
    stop_event: threading.Event,
) -> None:
    """
    Reads frames from `source` (file path, camera index, or RTSP URL) and
    pushes them into the bounded frame_queue. Blocks on put() when the queue
    is full — this IS the backpressure: capture slows to match processing
    instead of OOM-ing on unbounded buffering.

    Puts None as a sentinel when the stream ends or stop_event fires.
    Zero changes needed here to switch from a file to a live camera/RTSP URL.
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        frame_queue.put(None)
        logger.error("Cannot open video source: %s", source)
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0 or math.isinf(fps):
        fps = 30.0
    frame_delay = 1.0 / fps

    while not stop_event.is_set():
        start_t = time.time()
        
        ok, frame = cap.read()
        if not ok:
            break
        
        # Non-blocking, frame-dropping behavior for real-time compliance
        try:
            frame_queue.put_nowait(frame)
        except queue.Full:
            try:
                frame_queue.get_nowait()  # Drop the oldest frame
            except queue.Empty:
                pass
            try:
                frame_queue.put_nowait(frame) # Put the new frame
            except queue.Full:
                pass
                
        # Simulate real-time stream if reading from a fast local video file
        elapsed = time.time() - start_t
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)

    frame_queue.put(None)  # sentinel: real end of stream
    cap.release()


# ─────────────────────────────────────────────────────────────────────────────
# Alert event schema
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AlertEvent:
    """
    Emitted when a tracked vehicle's resolved plate matches the watchlist.
    All confidence values are in [0, 1]. combined_confidence = OCR conf × fuzzy
    match score, giving operators a single trust number instead of a boolean.
    """
    track_id: int
    camera_id: str
    plate: str
    matched_watchlist_plate: str
    reason: str
    fuzzy_match_score: float        # [0, 100] → normalised to [0, 1] in API
    plate_ocr_confidence: float     # avg OCR confidence for this plate
    combined_confidence: float      # (fuzzy_score/100) × ocr_conf
    frame_idx: int
    timestamp: float                # Unix timestamp

    def to_dict(self) -> Dict:
        return {
            "track_id": self.track_id,
            "camera_id": self.camera_id,
            "plate": self.plate,
            "matched_watchlist_plate": self.matched_watchlist_plate,
            "reason": self.reason,
            "fuzzy_match_score": round(self.fuzzy_match_score, 2),
            "plate_ocr_confidence": round(self.plate_ocr_confidence, 4),
            "combined_confidence": round(self.combined_confidence, 4),
            "frame_idx": self.frame_idx,
            "timestamp": self.timestamp,
            "event_type": "WATCHLIST_ALERT",
        }


@dataclass
class DetectionEvent:
    """Emitted for every tracked vehicle on every processed frame."""
    track_id: int
    camera_id: str
    plate: Optional[str]
    plate_confidence: float
    vehicle_bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    frame_idx: int
    timestamp: float
    is_resolved: bool  # True once CONFIDENT_VOTE_COUNT reached

    def to_dict(self) -> Dict:
        return {
            "track_id": self.track_id,
            "camera_id": self.camera_id,
            "plate": self.plate,
            "plate_confidence": round(self.plate_confidence, 4),
            "vehicle_bbox": list(self.vehicle_bbox),
            "frame_idx": self.frame_idx,
            "timestamp": self.timestamp,
            "is_resolved": self.is_resolved,
            "event_type": "VEHICLE_DETECTED",
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline class
# ─────────────────────────────────────────────────────────────────────────────

class ANPRPipeline:
    """
    Streaming ANPR + multi-object tracking pipeline.

    Instantiate once, call start() to begin processing, stop() to shut down.
    Results are delivered via the on_alert and on_detection callbacks —
    wire these to your FastAPI WebSocket broadcaster or DB writer.

    Example:
        pipeline = ANPRPipeline(camera_id="CAM-01", watchlist=wl)
        pipeline.on_alert = lambda evt: broadcast_ws(evt.to_dict())
        pipeline.on_detection = lambda evt: save_to_db(evt.to_dict())
        pipeline.start(source=0)   # 0 = default webcam
        ...
        pipeline.stop()
    """

    def __init__(
        self,
        camera_id: str = "CAM-UNKNOWN",
        watchlist: Optional[Watchlist] = None,
        vehicle_model_path: str = "yolov8n.pt",
        plate_model_repo: str = "Koushim/yolov8-license-plate-detection",
        plate_model_file: str = "best.pt",
        show_preview: bool = False,
    ) -> None:
        self.camera_id = camera_id
        self.watchlist = watchlist or Watchlist()

        self._vehicle_model_path = vehicle_model_path
        self._plate_model_repo = plate_model_repo
        self._plate_model_file = plate_model_file
        self.show_preview = show_preview

        # Callbacks — set before calling start()
        self.on_alert: Optional[Callable[[AlertEvent], None]] = None
        self.on_detection: Optional[Callable[[DetectionEvent], None]] = None

        self._stop_event = threading.Event()
        self._processing_thread: Optional[threading.Thread] = None
        self._running = False

    def start(self, source: Any = 0) -> None:
        """
        Start the pipeline in a background thread. Returns immediately.
        source: camera index (int), video file path (str), or RTSP URL (str).
        """
        if self._running:
            logger.warning("Pipeline already running for %s", self.camera_id)
            return

        _load_models(
            vehicle_model_path=self._vehicle_model_path,
            plate_model_repo=self._plate_model_repo,
            plate_model_file=self._plate_model_file,
        )

        self._stop_event.clear()
        self._source = source
        self._processing_thread = threading.Thread(
            target=self._run_pipeline,
            args=(source,),
            daemon=True,
            name=f"anpr-pipeline-{self.camera_id}",
        )
        self._processing_thread.start()
        self._running = True
        logger.info("ANPR pipeline started for camera %s, source: %s", self.camera_id, source)

    def stop(self) -> None:
        """Signal the pipeline to stop and wait for the thread to exit."""
        self._stop_event.set()
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=10)
        self._running = False
        logger.info("ANPR pipeline stopped for camera %s", self.camera_id)

    @property
    def is_running(self) -> bool:
        return self._running and (
            self._processing_thread is not None
            and self._processing_thread.is_alive()
        )

    def _run_pipeline(self, source: Any) -> None:
        """
        Internal main loop. Called in a daemon thread by start().

        Structure:
          ┌─ capture thread ─────────────────────────────────────┐
          │  VideoCapture → frame_queue (bounded, backpressure)   │
          └───────────────────────────────────────────────────────┘
                               ↓ (blocks on get)
          ┌─ main loop (this thread) ─────────────────────────────┐
          │  YOLO vehicle detect + ByteTrack (single-threaded)     │
          │  → dispatch plate OCR to ThreadPoolExecutor            │
          │  → collect futures (non-blocking) + update TrackState  │
          │  → check watchlist → emit callbacks                    │
          └───────────────────────────────────────────────────────┘
        """
        from ultralytics import YOLO

        frame_queue: "queue.Queue[Optional[np.ndarray]]" = queue.Queue(
            maxsize=FRAME_QUEUE_MAXSIZE
        )

        cap_thread = threading.Thread(
            target=_capture_thread_fn,
            args=(source, frame_queue, self._stop_event),
            daemon=True,
        )
        cap_thread.start()

        # Reset ByteTrack IDs so each pipeline run starts from track #1
        try:
            from ultralytics.trackers.basetrack import BaseTrack
            BaseTrack.reset_id()
        except Exception:
            pass

        # Use ProcessPoolExecutor to bypass GIL
        ocr_executor = ProcessPoolExecutor(
            max_workers=OCR_WORKER_THREADS,
            initializer=_init_worker,
            initargs=(self._plate_model_repo, self._plate_model_file)
        )
        pending_futures: Dict[int, Future] = {}  # track_id → in-flight OCR future
        track_states: Dict[int, TrackState] = defaultdict(TrackState)
        frame_idx = 0

        try:
            while not self._stop_event.is_set():
                try:
                    frame = frame_queue.get(timeout=2.0)
                except queue.Empty:
                    continue

                if frame is None:  # sentinel: stream ended
                    break

                frame_idx += 1
                self._process_frame(
                    frame=frame,
                    frame_idx=frame_idx,
                    pending_futures=pending_futures,
                    track_states=track_states,
                    ocr_executor=ocr_executor,
                )

        except Exception as exc:
            logger.error("Pipeline error (camera %s): %s", self.camera_id, exc, exc_info=True)
        finally:
            self._stop_event.set()
            ocr_executor.shutdown(wait=True)
            self._running = False
            if self.show_preview:
                import cv2
                cv2.destroyAllWindows()
            logger.info(
                "Pipeline finished for %s after %d frames", self.camera_id, frame_idx
            )

    def _process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int,
        pending_futures: Dict[int, Future],
        track_states: Dict[int, TrackState],
        ocr_executor: ThreadPoolExecutor,
    ) -> None:
        """
        Process one frame:
          1. Collect finished OCR futures (non-blocking) → update TrackState.
          2. Run YOLO vehicle detection + ByteTrack.
          3. For each track, maybe dispatch a new OCR job.
          4. Resolve each track's plate, check watchlist, fire callbacks.

        NOTE: Annotated overlay is built on a copy of the raw frame. Vehicle
        crops for OCR are taken from the CLEAN `frame`, not the annotated copy —
        otherwise drawn bounding boxes and labels from nearby vehicles end up
        inside other tracks' plate crops (this was a real bug in the notebook's
        earlier version).
        """
        global _vehicle_model

        # ── Step 1: pick up completed OCR results ─────────────────────────────
        for tid in list(pending_futures.keys()):
            fut = pending_futures[tid]
            if fut.done():
                try:
                    plate, conf = fut.result()
                    state = track_states[tid]
                    
                    if plate and conf >= MIN_ACCEPT_CONFIDENCE:
                        state.add_reading(plate, conf)
                        logger.debug(
                            "[frame %d] CAM=%s TID=%d OCR: %s (%.0f%%)",
                            frame_idx, self.camera_id, tid, plate, conf * 100,
                        )
                        # Aggressive early exit if confidence is very high
                        if conf >= EARLY_EXIT_CONFIDENCE:
                            state.ocr_locked = True
                            logger.info("TID=%d: OCR locked by high confidence (%.2f)", tid, conf)
                    else:
                        state.unreadable_strikes += 1
                        if state.unreadable_strikes >= UNREADABLE_STRIKES_LIMIT:
                            state.ocr_locked = True
                            logger.info("TID=%d: OCR locked by unreadable strikes", tid)
                            
                except Exception as exc:
                    logger.debug("OCR future error TID=%d: %s", tid, exc)
                del pending_futures[tid]

        # ── Step 2: vehicle detection + tracking (with Frame Skipping) ────────
        if frame_idx % SKIP_FRAMES == 0 or not hasattr(self, "_last_boxes"):
            results = _vehicle_model.track(
                frame,
                persist=True,
                classes=VEHICLE_CLASS_IDS,
                verbose=False,
                device=_DEVICE,
            )
            if results[0].boxes.id is not None:
                self._last_boxes = results[0].boxes.xyxy.cpu().numpy()
                self._last_ids = results[0].boxes.id.cpu().numpy().astype(int)
            else:
                self._last_boxes = np.array([])
                self._last_ids = np.array([])

        boxes = self._last_boxes
        track_ids = self._last_ids

        if len(boxes) == 0:
            return  # no tracks this frame

        timestamp = time.time()

        for box, tid in zip(boxes, track_ids):
            x1, y1, x2, y2 = map(int, box)
            tid = int(tid)
            state = track_states[tid]
            state.frames_seen += 1

            # ── Step 3: dispatch OCR if due ───────────────────────────────────
            needs_ocr = (
                state.frames_seen % OCR_SAMPLE_INTERVAL == 0
                and tid not in pending_futures
                and not state.ocr_locked
            )
            if needs_ocr:
                crop = frame[max(0, y1):y2, max(0, x1):x2].copy()
                pending_futures[tid] = ocr_executor.submit(
                    get_plate_reading, crop, tid
                )

            # ── Step 4: resolve plate, check watchlist, emit callbacks ────────
            resolved_plate, plate_conf = state.resolved_plate()

            # Detection event (every frame for every track)
            if self.on_detection:
                evt = DetectionEvent(
                    track_id=tid,
                    camera_id=self.camera_id,
                    plate=resolved_plate,
                    plate_confidence=plate_conf,
                    vehicle_bbox=(x1, y1, x2, y2),
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    is_resolved=state.is_confidently_resolved(),
                )
                try:
                    self.on_detection(evt)
                except Exception:
                    pass

            # Watchlist check — emit alert at most once per track
            if resolved_plate and not state.alerted:
                match_entry, match_score = self.watchlist.check(resolved_plate)
                if match_entry:
                    state.alerted = True
                    alert = AlertEvent(
                        track_id=tid,
                        camera_id=self.camera_id,
                        plate=resolved_plate,
                        matched_watchlist_plate=match_entry["raw"],
                        reason=match_entry["reason"],
                        fuzzy_match_score=match_score,
                        plate_ocr_confidence=plate_conf,
                        combined_confidence=(match_score / 100.0) * plate_conf,
                        frame_idx=frame_idx,
                        timestamp=timestamp,
                    )
                    logger.warning(
                        "WATCHLIST ALERT: camera=%s plate=%s matched=%s score=%.0f%% "
                        "combined_conf=%.2f",
                        self.camera_id, resolved_plate, match_entry["raw"],
                        match_score, alert.combined_confidence,
                    )
                    if self.on_alert:
                        try:
                            self.on_alert(alert)
                        except Exception:
                            pass

        if self.show_preview:
            import cv2
            preview_frame = frame.copy()
            for box, tid in zip(boxes, track_ids):
                x1, y1, x2, y2 = map(int, box)
                state = track_states[tid]
                resolved_plate, plate_conf = state.resolved_plate()
                
                label = f"ID:{tid}"
                color = (0, 255, 0)
                if resolved_plate:
                    label += f" {resolved_plate} ({plate_conf*100:.0f}%)"
                    if state.alerted:
                        color = (0, 0, 255) # Red for alert
                elif state.ocr_locked:
                    label += " (locked)"
                
                cv2.rectangle(preview_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(preview_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
            cv2.imshow(f"ANPR Preview - {self.camera_id}", preview_frame)
            cv2.waitKey(1)


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import json

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="God's Eye — ANPR pipeline test")
    parser.add_argument("--source", default="0",
                        help="Video source: camera index (0), file path, or RTSP URL")
    parser.add_argument("--camera-id", default="CAM-TEST")
    parser.add_argument("--watchlist", nargs="*", metavar="PLATE",
                        help="Plates to add to watchlist for testing")
    parser.add_argument("--output", default=None, help="Optional annotated output video path")
    parser.add_argument("--show", action="store_true", help="Show real-time annotated video stream")
    args = parser.parse_args()

    source: Any = int(args.source) if args.source.isdigit() else args.source

    wl = Watchlist()
    if args.watchlist:
        for p in args.watchlist:
            wl.add(p, reason="CLI test")

    alerts_collected: List[Dict] = []
    detections_collected: List[Dict] = []

    pipeline = ANPRPipeline(camera_id=args.camera_id, watchlist=wl, show_preview=args.show)
    pipeline.on_alert = lambda evt: (
        alerts_collected.append(evt.to_dict()),
        print("ALERT:", json.dumps(evt.to_dict(), indent=2))
    )
    pipeline.on_detection = lambda evt: detections_collected.append(evt.to_dict())

    pipeline.start(source=source)

    print(f"Pipeline running for camera {args.camera_id}. Press Ctrl+C to stop.")
    try:
        while pipeline.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    pipeline.stop()

    print(f"\nDone. {len(alerts_collected)} alert(s), {len(detections_collected)} detection events.")
    if alerts_collected:
        with open("alerts_output.json", "w") as f:
            json.dump(alerts_collected, f, indent=2)
        print("Alerts saved to alerts_output.json")
