from __future__ import annotations

import argparse
import csv
import json
import os
import socket
import struct
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.trackers import BYTETracker
import types
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_VEHICLE_MODEL = PROJECT_ROOT / "yolov8n.pt"

DEFAULT_PLATE_MODEL = (
    PROJECT_ROOT / "models" / "plate_detector" / "weights" / "best.pt"
)

OCR_HOST = "127.0.0.1"
OCR_PORT = 8765

VEHICLE_CLASSES = [2, 3, 5, 7]


from app.realtime.ocr_worker import OCRClient, OCRWorker
from app.realtime.capture import LiveCapture
from app.anpr.temporal_fusion import (
    MultiTrackBuffer,
    make_observation,
    fuse_observations,
    get_telemetry,
)

# ================================================================
# LATENCY & STABILIZATION
# ================================================================

import collections
import statistics
import numpy as np

# ================================================================
# MJPEG STREAMING SERVER
# ================================================================
import http.server
import socketserver
import io

class MJPEGStreamHandler(http.server.BaseHTTPRequestHandler):
    global_jpeg_buffer = b""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head><title>ANPR Live</title></head><body><img src="/video" style="width:100%; max-width:1280px;"></body></html>')
            return
            
        if self.path == '/video':
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    jpeg = MJPEGStreamHandler.global_jpeg_buffer
                    if jpeg:
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(jpeg)))
                        self.end_headers()
                        self.wfile.write(jpeg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.033)
            except Exception:
                pass
            return
            
        self.send_response(404)
        self.end_headers()

def start_mjpeg_server(port=5000):
    class DualStackServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True
    
    try:
        httpd = DualStackServer(('0.0.0.0', port), MJPEGStreamHandler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        print(f"MJPEG server started at http://localhost:{port}")
    except Exception as e:
        print(f"Failed to start MJPEG server: {e}")


class TrackLatency:
    def __init__(self, start_mono, start_pts):
        self.first_seen_monotonic = start_mono
        self.first_seen_pts = start_pts
        self.first_plate_attempt_monotonic = None
        self.plate_attempts = 0
        self.plate_eligible_frames = 0
        self.vehicle_detections = 0
        self.last_seen_monotonic = start_mono
        self.last_seen_pts = start_pts
        self.first_plate_attempt_pts = None
        self.first_plate_detection_monotonic = None
        self.first_plate_detection_pts = None
        self.first_usable_plate_monotonic = None
        self.first_usable_plate_pts = None
        self.first_ocr_submit_monotonic = None
        self.first_ocr_submit_pts = None
        self.first_ocr_result_monotonic = None
        self.first_ocr_result_pts = None
        self.confirmed_monotonic = None
        self.confirmed_pts = None
        self.track_end_monotonic = None
        self.track_end_pts = None
        self.latency_cause = "NO_PLATE"

class PlateBoxStabilizer:
    def __init__(self, max_len=5):
        self.history = collections.deque(maxlen=max_len)
    def smooth(self, x1, y1, x2, y2):
        self.history.append((x1, y1, x2, y2))
        return (int(statistics.median([b[0] for b in self.history])),
                int(statistics.median([b[1] for b in self.history])),
                int(statistics.median([b[2] for b in self.history])),
                int(statistics.median([b[3] for b in self.history])))

def crops_are_duplicates(c1, c2, thresh=15.0):
    if c1 is None or c2 is None: return False
    import cv2
    if c1.shape != c2.shape: c2 = cv2.resize(c2, (c1.shape[1], c1.shape[0]))
    g1, g2 = cv2.cvtColor(c1, cv2.COLOR_BGR2GRAY), cv2.cvtColor(c2, cv2.COLOR_BGR2GRAY)
    return np.mean(np.abs(g1.astype(np.float32) - g2.astype(np.float32))) < thresh

# ================================================================
# QUALITY
# ================================================================

def sharpness(crop: np.ndarray) -> float:
    if crop is None or crop.size == 0:
        return 0.0
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def quality_score(crop: np.ndarray) -> float:
    if crop is None or crop.size == 0:
        return 0.0
    h, w = crop.shape[:2]
    sharp = min(sharpness(crop) / 400.0, 1.0)
    size = min((w * h) / 8000.0, 1.0)
    aspect = w / max(h, 1)
    geometry = 1.0 if 1.5 <= aspect <= 8.0 else 0.0
    return float(0.55 * sharp + 0.30 * size + 0.15 * geometry)


# ================================================================
# LETTERBOX HELPERS
# ================================================================

def letterbox(img, new_shape=(416, 416), color=(114, 114, 114)):
    shape = img.shape[:2]
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    dw /= 2
    dh /= 2
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top = int(round(dh - 0.1))
    bottom = int(round(dh + 0.1))
    left = int(round(dw - 0.1))
    right = int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, r, (dw, dh)


def scale_boxes(boxes, r, pad):
    dw, dh = pad
    boxes[:, [0, 2]] -= dw
    boxes[:, [1, 3]] -= dh
    boxes /= r
    return boxes


# ================================================================
# MAIN RUN
# ================================================================

def run(args):

    # ============================================================
    # DEVICE SETUP
    # ============================================================

    use_gpu = torch.cuda.is_available()
    device = 0 if use_gpu else "cpu"
    use_half = use_gpu

    print("=" * 70)
    print("REALTIME ANPR V2 — Phase I (Low Latency)")
    print("=" * 70)
    print(f"Source             : {args.source}")
    print(f"Vehicle model      : {args.vehicle_model}")
    print(f"Plate model        : {args.plate_model}")
    print(f"Device             : {device}")
    print(f"Vehicle imgsz      : {args.vehicle_imgsz}")
    print(f"Plate imgsz        : {args.plate_imgsz}")
    print(f"Plate cadence      : {args.plate_cadence}")
    print(f"Plate track cooldown: {args.plate_track_cooldown}")
    print(f"Min vehicle W/H    : {args.min_vehicle_width}/{args.min_vehicle_height}")
    print(f"OCR spacing        : {args.ocr_spacing}")
    print(f"Plate batch        : {args.plate_batch_size}")
    print("=" * 70)

    # ============================================================
    # LOAD MODELS
    # ============================================================

    vehicle_model = YOLO(args.vehicle_model)
    plate_model = YOLO(args.plate_model)

    # Explicitly convert to FP16 on GPU.
    # The 'half' argument to track/predict is deprecated in modern Ultralytics
    # and does NOT reliably set model dtype. Use model.model.half() directly.
    if use_gpu:
        vehicle_model.model.half()
        plate_model.model.half()
        print(f"  vehicle dtype: {next(vehicle_model.model.parameters()).dtype}")
        print(f"  plate dtype  : {next(plate_model.model.parameters()).dtype}")

    # ============================================================
    # OCR
    # ============================================================

    ocr_client = OCRClient()
    ocr_worker = OCRWorker(ocr_client, max_queue=8).start()

    # ============================================================
    # CAPTURE
    # ============================================================

    capture = LiveCapture(args.source).start()

    # ============================================================
    # STATE
    # ============================================================

    last_plate_detection = {}   # track_id -> last frame plate YOLO ran for it
    last_ocr_submit = {}        # track_id -> last frame OCR was submitted
    current_frame_results = {}  # track_id -> {text, confidence} for this frame only

    track_latencies = {}
    plate_stabilizers = {}
    last_submitted_crops = {}
    completed_track_metrics = []
    
    ocr_duplicate_skips = 0
    ocr_unique_submissions = 0
    track_buffer = MultiTrackBuffer(max_per_track=12)
    pending_ocr_metadata = {}   # (frame_id, track_id) -> {"quality_score", "detector_confidence", "submitted_at"}
    fused_results = {}          # track_id -> FusionResult

    # ============================================================
    # OUTPUT
    # ============================================================

    csv_file = None
    csv_writer = None

    if args.csv and not args.performance_mode:
        csv_file = open(args.csv, "w", newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["frame_id", "timestamp", "track_id", "vehicle_class", "vehicle_confidence", "plate_bbox", "plate_text", "ocr_confidence", "fused_plate", "fused_confidence"])

    # Start the MJPEG Server if we are not in performance mode
    if not args.performance_mode:
        start_mjpeg_server(port=5000)

    print()
    print("=" * 70)
    print(f"STARTING LOW-LATENCY ANPR V2 PIPELINE (Phase F)")
    print(f"Source: {args.source}")

    output_writer = None

    # ============================================================
    # COUNTERS
    # ============================================================

    processed = 0
    vehicle_detections = 0
    plate_detections = 0
    ocr_submissions = 0
    ocr_results = 0
    orphan_ocr_results = 0

    # ============================================================
    # TIMERS & TELEMETRY
    # ============================================================

    start_time = time.perf_counter()

    # Phase E — wall-clock per stage (accumulated, then divided by processed)
    capture_read_ms_total     = 0.0
    capture_sleep_ms_total    = 0.0
    ocr_check_ms_total        = 0.0
    vehicle_track_ms_total    = 0.0
    vehicle_result_ms_total   = 0.0
    plate_batch_build_ms_total  = 0.0
    plate_predict_ms_total    = 0.0
    plate_result_ms_total     = 0.0
    ocr_submit_ms_total       = 0.0
    drawing_display_ms_total  = 0.0
    other_loop_ms_total       = 0.0
    total_frame_wall_ms_total = 0.0

    # Frame freshness / age
    frame_ages = []

    # Vehicle inference breakdown (from YOLO speed dict)
    vehicle_predict_calls         = 0
    vehicle_preprocess_ms_total   = 0.0
    vehicle_inference_ms_total    = 0.0
    vehicle_postprocess_ms_total  = 0.0
    vehicle_tracker_ms_total      = 0.0
    vehicle_total_ms_total        = 0.0

    # Plate inference breakdown (from YOLO speed dict)
    plate_predict_calls      = 0
    plate_inference_images   = 0
    plate_inference_batches  = 0
    plate_preprocess_ms      = 0.0
    plate_infer_ms           = 0.0
    plate_postprocess_ms     = 0.0
    plate_time_total         = 0.0

    # Phase F — plate eligibility counters
    plate_tracks_considered       = 0
    plate_tracks_submitted        = 0
    plate_tracks_skipped_cooldown = 0
    plate_tracks_skipped_size     = 0

    # Misc
    no_raw_vehicle = 0
    rejected_class = 0
    rejected_confidence = 0
    no_track_id = 0
    small_vehicle = 0
    tracked_vehicle = 0
    capture_dropped       = 0
    frames_since_report   = 0
    active_tracks         = 0
    track_creations       = 0
    track_id_disappearances = 0
    ocr_submitted         = 0
    ocr_jobs_dropped      = 0
    ocr_round_trip_total  = 0.0
    total_lag             = 0.0

    # ============================================================
    # WARMUP & TRACKER
    # ============================================================

    print("="*60)
    print("REACHED BEFORE LOADED BYTETRACK CONFIGURATION:", flush=True)
    print("LOADED BYTETRACK CONFIGURATION:", flush=True)
    with open(PROJECT_ROOT / "configs" / "bytetrack_anpr_live.yaml") as f:
        tracker_config = yaml.safe_load(f)
    for k, v in tracker_config.items():
        print(f"  {k}: {v}")
    print("="*60)
    tracker_args = types.SimpleNamespace(**tracker_config)
    tracker = BYTETracker(tracker_args)


    print("Warming up GPU...", flush=True)

    dummy = np.zeros((640, 640, 3), dtype=np.uint8)

    vehicle_model.predict(
        dummy,
        imgsz=args.vehicle_imgsz,
        device=device,
        verbose=False,
    )

    plate_model.predict(
        [dummy],
        imgsz=args.plate_imgsz,
        device=device,
        verbose=False,
    )

    if use_gpu:
        torch.cuda.synchronize()

    print("Warmup complete.", flush=True)

    # ============================================================
    # MAIN LOOP
    # ============================================================

    while not capture.stop_event.is_set():

        # --------------------------------------------------------
        # CAPTURE READ (timed)
        # --------------------------------------------------------
        _t_loop_start = time.perf_counter()

        item = capture.read()

        _t_after_read = time.perf_counter()
        capture_read_ms_total += (_t_after_read - _t_loop_start) * 1000.0

        if item is None:
            time.sleep(0.001)
            capture_sleep_ms_total += (time.perf_counter() - _t_after_read) * 1000.0
            continue

        frame_id, frame, capture_ts = item
        current_monotonic = time.perf_counter()
        current_pts = frame.pts_ms if hasattr(frame, 'pts_ms') else current_monotonic * 1000

        # Auto-rotate portrait frames to landscape so YOLO sees correct orientation.
        # IP Webcam sends portrait (H > W) when phone is held vertically.
        h_fr, w_fr = frame.shape[:2]
        if h_fr > w_fr:
            if args.rotate == 'cw':
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            else:  # default: ccw
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Frame-age
        processing_ts = time.perf_counter()
        frame_age_ms = (processing_ts - capture_ts) * 1000.0
        frame_ages.append(frame_age_ms)

        frame_start = processing_ts
        processed += 1
        frames_since_report += 1

        # --------------------------------------------------------
        # READ OCR RESULTS — non-blocking pop (timed)
        # --------------------------------------------------------
        _t_ocr_chk = time.perf_counter()

        incoming_results = ocr_worker.pop_results()
        current_frame_results.clear()

        for result in incoming_results:
            result_frame  = int(result["frame_id"])
            res_track_id  = int(result["track_id"])
            text          = str(result["text"])
            confidence    = float(result["confidence"])

            # Phase G: Extract metadata for fusion
            meta = pending_ocr_metadata.pop((result_frame, res_track_id), None)
            if not meta:
                orphan_ocr_results += 1
                continue
            
            # Phase G: Track-level fusion
            obs = make_observation(
                frame_id=result_frame,
                track_id=res_track_id,
                raw_text=text,
                ocr_confidence=confidence,
                quality_score=meta["quality_score"],
                detector_confidence=meta["detector_confidence"],
                timestamp=meta["submitted_at"]
            )
            track_buffer.add(obs)
            
            lat = track_latencies.get(res_track_id)
            if lat and not lat.first_ocr_result_monotonic:
                lat.first_ocr_result_monotonic = current_monotonic
                lat.first_ocr_result_pts = current_pts

            fused_res = fuse_observations(track_buffer.get(res_track_id), track_id=res_track_id)
            fused_results[res_track_id] = fused_res
            
            if fused_res.decision == "CONFIRMED" and lat and not lat.confirmed_monotonic:
                lat.confirmed_monotonic = current_monotonic
                lat.confirmed_pts = current_pts


            # Exact-frame semantics: only update current-frame visualization if frame matches exactly
            if result_frame == frame_id:
                current_frame_results[res_track_id] = {
                    "text": text,
                    "confidence": confidence,
                }

            # CSV log (every valid incoming OCR row logs both its current observation and the updated fused state)
            if csv_writer and not args.performance_mode:
                csv_writer.writerow([
                    result_frame, res_track_id, text, f"{confidence:.4f}",
                    f"{meta['quality_score']:.4f}", f"{meta['detector_confidence']:.4f}",
                    fused_res.fused_text if fused_res.fused_text else "",
                    f"{fused_res.confidence:.4f}", fused_res.decision,
                    fused_res.supporting_obs_count,
                    json.dumps(fused_res.supporting_frame_ids),
                    fused_res.best_evidence_frame if fused_res.best_evidence_frame else ""
                ])

            ocr_results += 1

        # Phase G: Expire stale pending OCR metadata to prevent memory leaks if OCR drops a frame
        now = time.perf_counter()
        stale_pending = [k for k, v in pending_ocr_metadata.items() if (now - v["submitted_at"]) > 5.0]
        for k in stale_pending:
            del pending_ocr_metadata[k]

        ocr_check_ms_total += (time.perf_counter() - _t_ocr_chk) * 1000.0

        # --------------------------------------------------------
        # VEHICLE TRACKING (timed)
        # --------------------------------------------------------
        if args.debug and processed % 90 == 0:
            dbg_path = PROJECT_ROOT / "outputs" / "live_debug"
            dbg_path.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(dbg_path / f"frame_{processed}.jpg"), frame)
            h, w = frame.shape[:2]
            print(f"DEBUG_FRAME: frame_id={processed} resolution={w}x{h}")

        _t_veh_start = time.perf_counter()

        results = vehicle_model.predict(
            frame,
            conf=max(0.01, args.vehicle_conf * 0.5),  # BUG-10 FIX: use near-args conf, not hardcoded 0.01
            imgsz=args.vehicle_imgsz,
            device=device,
            verbose=False,
        )

        _t_veh_end = time.perf_counter()
        vehicle_track_ms_total += (_t_veh_end - _t_veh_start) * 1000.0
        vehicle_total_ms_total += (_t_veh_end - _t_veh_start) * 1000.0

        result = results[0]
        vehicle_predict_calls += 1

        if hasattr(result, "speed"):
            vehicle_preprocess_ms_total  += result.speed.get("preprocess", 0.0)
            vehicle_inference_ms_total   += result.speed.get("inference", 0.0)
            vehicle_postprocess_ms_total += result.speed.get("postprocess", 0.0)

        # --------------------------------------------------------
        # VEHICLE RESULT PROCESSING (timed — .cpu()/.numpy() here)
        # --------------------------------------------------------
        _t_veh_res = time.perf_counter()

        tracks = []
        raw_boxes = result.boxes.data.detach().cpu().numpy()
        raw_detection_count = len(raw_boxes)

        class_filtered = [b for b in raw_boxes if int(b[5]) in VEHICLE_CLASSES]
        vehicle_class_filtered_count = len(class_filtered)

        conf_filtered = [b for b in class_filtered if b[4] >= args.vehicle_conf]
        vehicle_conf_filtered_count = len(conf_filtered)

        if args.debug:
            for b in raw_boxes:
                x1, y1, x2, y2, c, cls = b
                cls_int = int(cls)
                if cls_int not in VEHICLE_CLASSES:
                    print(f"FILTERED: class={cls_int} conf={c:.3f} bbox=({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}) reason=WRONG_CLASS")
                elif c < args.vehicle_conf:
                    print(f"FILTERED: class={cls_int} conf={c:.3f} bbox=({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}) reason=LOW_CONFIDENCE")
                else:
                    print(f"RAW: class={cls_int} conf={c:.3f} bbox=({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)})")

        if len(conf_filtered) > 0:
            det_tensor = torch.tensor(np.array(conf_filtered), dtype=torch.float32, device="cpu")
            from ultralytics.engine.results import Boxes
            det_boxes = Boxes(det_tensor, orig_shape=frame.shape[:2])
            tracked_stracks = tracker.update(det_boxes, frame)
            tracker_output_count = len(tracked_stracks)

            for t in tracked_stracks:
                x1, y1, x2, y2 = float(t[0]), float(t[1]), float(t[2]), float(t[3])
                tid = int(t[4])
                conf = float(t[5])
                w = x2 - x1
                h = y2 - y1
                if tid not in plate_stabilizers:
                    plate_stabilizers[tid] = PlateBoxStabilizer()
                tracks.append((tid, float(conf), (int(x1), int(y1), int(x2), int(y2))))
                if args.debug:
                    print(f"TRACK: id={tid} conf={conf:.3f} bbox=({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}) size={int(w)}x{int(h)}")

                if tid not in track_latencies:
                    track_latencies[tid] = TrackLatency(current_monotonic, current_pts)
                track_latencies[tid].vehicle_detections += 1
                track_latencies[tid].last_seen_monotonic = current_monotonic
                track_latencies[tid].last_seen_pts = current_pts

        # Snapshot tracker state (read-only, no modification)
        active_ids = {t.track_id for t in tracker.tracked_stracks}
        active_ids.update({t.track_id for t in tracker.lost_stracks})

        active_tracks = len(tracker.tracked_stracks)
        track_creations = (
            len(tracker.tracked_stracks)
            + len(tracker.lost_stracks)
            + len(tracker.removed_stracks)
        )

        vehicle_result_ms_total += (time.perf_counter() - _t_veh_res) * 1000.0

        # --------------------------------------------------------
        # PRUNE STALE TRACK IDs — runs UNCONDITIONALLY (BUG-7/8 FIX)
        # Always compute current_ids: use active tracks from BYTETracker
        # (not just from this frame's detections, since tracks may be
        # predicted-forward even when there's no fresh detection)
        # --------------------------------------------------------
        current_ids = {t[0] for t in tracks} if tracks else set()

        stale = [k for k in last_plate_detection if k not in current_ids]
        for k in stale:
            del last_plate_detection[k]
        stale_ocr = [k for k in last_ocr_submit if k not in current_ids]
        for k in stale_ocr:
            del last_ocr_submit[k]

        # Phase G pruning — use active_ids from BYTETracker for more accurate pruning
        track_buffer.prune(active_ids)

        # Track End finalization — BUG-8 FIX: run unconditionally, using BYTETracker active_ids
        stale_fused = [k for k in fused_results if k not in active_ids]
        for tid in stale_fused:
            # Track ended!
            lat = track_latencies.get(tid)
            if lat:
                lat.track_end_monotonic = current_monotonic
                lat.track_end_pts = current_pts
                if not lat.confirmed_monotonic:
                    f_res = fuse_observations(track_buffer.get(tid), track_id=tid)
                    if f_res and f_res.decision != "UNREADABLE":
                        lat.latency_cause = "FUSION_THRESHOLD_WAITING_END"
                    else:
                        lat.latency_cause = "UNREADABLE_OR_NO_OCR"
                else:
                    lat.latency_cause = "CONFIRMED"
                completed_track_metrics.append(lat)
                if args.debug:
                    print(f"\nTRACK END id={tid} "
                          f"lifetime={lat.track_end_pts - lat.first_seen_pts:.0f}ms "
                          f"veh_det={lat.vehicle_detections} "
                          f"ocr={'YES' if lat.first_ocr_result_pts else 'NO'} "
                          f"cause={lat.latency_cause}")
                del track_latencies[tid]
            del fused_results[tid]

        # Also clean up expired from track_latencies for tracks that never had fused_results
        stale_latencies = [tid for tid in track_latencies if tid not in active_ids and tid not in {t[0] for t in tracks}]
        for tid in stale_latencies:
            lat = track_latencies[tid]
            lat.track_end_monotonic = current_monotonic
            lat.track_end_pts = current_pts
            lat.latency_cause = "LOST_NO_PLATE"
            completed_track_metrics.append(lat)
            del track_latencies[tid]


        # --------------------------------------------------------
        # BUILD PLATE-DETECTION BATCH — Phase F cadence gate
        # --------------------------------------------------------
        _t_batch_build = time.perf_counter()

        plate_inputs   = []
        plate_metadata = []

        is_plate_observation_frame = (frame_id % args.plate_cadence == 0)

        if is_plate_observation_frame and tracks:

            for (track_id, vehicle_conf, vehicle_box) in tracks:

                plate_tracks_considered += 1
                lat = track_latencies.get(track_id)
                if lat and not lat.first_plate_attempt_monotonic:
                    lat.first_plate_attempt_monotonic = current_monotonic
                    lat.first_plate_attempt_pts = current_pts

                # --- Per-track cooldown gate ---
                if args.plate_track_cooldown > 0:
                    last_det = last_plate_detection.get(track_id, -100000)
                    if frame_id - last_det < args.plate_track_cooldown:
                        plate_tracks_skipped_cooldown += 1
                        continue

                x1, y1, x2, y2 = vehicle_box

                # --- Vehicle size eligibility gate ---
                veh_w = x2 - x1
                veh_h = y2 - y1
                if veh_w < args.min_vehicle_width or veh_h < args.min_vehicle_height:
                    plate_tracks_skipped_size += 1
                    continue

                # --- Extract and validate crop ---
                vehicle_roi = frame[y1:y2, x1:x2]

                if vehicle_roi.size == 0:
                    continue

                # Accept this track
                last_plate_detection[track_id] = frame_id
                plate_tracks_submitted += 1

                plate_inputs.append(vehicle_roi)
                plate_metadata.append({
                    "track_id":    track_id,
                    "vehicle_conf": vehicle_conf,
                    "offset_x":    x1,
                    "offset_y":    y1,
                })

        elif is_plate_observation_frame and not tracks:
            # FULL-FRAME FALLBACK: no vehicle detected (phone too close / only plate visible).
            # Run plate detector on the entire frame using synthetic track_id=0.
            # This allows plate OCR even when YOLO misses the vehicle body.
            FALLBACK_TRACK_ID = 0
            last_det = last_plate_detection.get(FALLBACK_TRACK_ID, -100000)
            if frame_id - last_det >= args.ocr_spacing:
                if FALLBACK_TRACK_ID not in plate_stabilizers:
                    plate_stabilizers[FALLBACK_TRACK_ID] = PlateBoxStabilizer()
                if FALLBACK_TRACK_ID not in track_latencies:
                    track_latencies[FALLBACK_TRACK_ID] = TrackLatency(current_monotonic, current_pts)
                last_plate_detection[FALLBACK_TRACK_ID] = frame_id
                plate_tracks_submitted += 1
                plate_inputs.append(frame)
                plate_metadata.append({
                    "track_id":    FALLBACK_TRACK_ID,
                    "vehicle_conf": 1.0,
                    "offset_x":    0,
                    "offset_y":    0,
                })

        plate_batch_build_ms_total += (time.perf_counter() - _t_batch_build) * 1000.0

        # --------------------------------------------------------
        # BATCH PLATE DETECTION (timed)
        # --------------------------------------------------------
        _t_plate_pred = time.perf_counter()

        ocr_candidates = []

        if plate_inputs:

            plate_results = []
            batch_size    = args.plate_batch_size

            for i in range(0, len(plate_inputs), batch_size):
                chunk = plate_inputs[i : i + batch_size]

                plate_inference_batches += 1
                plate_inference_images  += len(chunk)
                plate_predict_calls     += 1

                # Manual letterbox so we control preprocessing exactly
                batch_imgs  = []
                batch_scales = []
                for img in chunk:
                    lb_img, r, pad = letterbox(img, (args.plate_imgsz, args.plate_imgsz))
                    batch_imgs.append(lb_img)
                    batch_scales.append((r, pad))

                chunk_results = plate_model.predict(
                    batch_imgs,
                    imgsz=args.plate_imgsz,
                    conf=args.plate_conf,
                    device=device,
                    verbose=False,
                )

                for r_idx, res in enumerate(chunk_results):
                    plate_preprocess_ms  += res.speed.get("preprocess", 0.0)
                    plate_infer_ms       += res.speed.get("inference", 0.0)
                    plate_postprocess_ms += res.speed.get("postprocess", 0.0)

                    # Unscale boxes back to original ROI coords
                    if res.boxes is not None and len(res.boxes) > 0:
                        r_val, pad = batch_scales[r_idx]
                        bxs = res.boxes.xyxy.cpu().numpy().copy()
                        bxs = scale_boxes(bxs, r_val, pad)
                        orig_h, orig_w = chunk[r_idx].shape[:2]
                        bxs[:, [0, 2]] = np.clip(bxs[:, [0, 2]], 0, orig_w)
                        bxs[:, [1, 3]] = np.clip(bxs[:, [1, 3]], 0, orig_h)
                        res.boxes_unscaled = bxs

                plate_results.extend(chunk_results)

            plate_time = time.perf_counter() - _t_plate_pred
            plate_time_total += plate_time

        plate_predict_ms_total += (time.perf_counter() - _t_plate_pred) * 1000.0

        # --------------------------------------------------------
        # PLATE RESULT PROCESSING (timed — .cpu()/.numpy() here)
        # --------------------------------------------------------
        _t_plate_res = time.perf_counter()

        if plate_inputs:
            for plate_result, meta in zip(plate_results, plate_metadata):

                # BUG-1 FIX: Extract track_id HERE, before any reference inside loops
                track_id = meta["track_id"]
                lat = track_latencies.get(track_id)

                if plate_result.boxes is None or len(plate_result.boxes) == 0:
                    continue

                # Use unscaled boxes if available, else fall back
                if hasattr(plate_result, "boxes_unscaled"):
                    boxes_arr   = plate_result.boxes_unscaled
                    conf_arr    = plate_result.boxes.conf.detach().cpu().numpy()
                else:
                    boxes_arr   = plate_result.boxes.xyxy.detach().cpu().numpy()
                    conf_arr    = plate_result.boxes.conf.detach().cpu().numpy()

                roi = plate_inputs[plate_metadata.index(meta)]

                best       = None
                best_score = -1.0

                for box, confidence in zip(boxes_arr, conf_arr):
                    px1, py1, px2, py2 = map(int, box)
                    px1 = max(0, px1)
                    py1 = max(0, py1)
                    px2 = min(roi.shape[1], px2)
                    py2 = min(roi.shape[0], py2)

                    if px2 <= px1 or py2 <= py1:
                        continue

                    if lat and not lat.first_plate_detection_monotonic:
                        lat.first_plate_detection_monotonic = current_monotonic
                        lat.first_plate_detection_pts = current_pts

                    # Stabilize Box — plate_stabilizers[track_id] is safe now (initialized on track create)
                    if track_id not in plate_stabilizers:
                        plate_stabilizers[track_id] = PlateBoxStabilizer()
                    sx1, sy1, sx2, sy2 = plate_stabilizers[track_id].smooth(px1, py1, px2, py2)
                    crop = roi[max(0, sy1):min(roi.shape[0], sy2), max(0, sx1):min(roi.shape[1], sx2)]

                    q = quality_score(crop)
                    score = 0.65 * float(confidence) + 0.35 * q

                    if score > best_score:
                        best_score = score
                        best = (crop, float(confidence), q)

                if best is None:
                    continue

                crop, plate_conf, quality = best
                plate_detections += 1

                last_ocr = last_ocr_submit.get(track_id, -100000)

                # OCR spacing gate
                if frame_id - last_ocr < args.ocr_spacing:
                    continue

                # Minimum crop width
                if crop.shape[1] < args.min_plate_width:
                    continue

                # Quality threshold
                if quality < args.min_quality:
                    continue

                
                # Duplicate suppression
                prev_crop_data = last_submitted_crops.get(track_id)
                skip = False
                if prev_crop_data:
                    p_crop, p_conf, p_q = prev_crop_data
                    if crops_are_duplicates(crop, p_crop) and quality < (p_q + 0.05) and float(plate_conf) < (p_conf + 0.05):
                        skip = True
                        ocr_duplicate_skips += 1
                
                if skip:
                    continue
                    
                ocr_unique_submissions += 1
                last_submitted_crops[track_id] = (crop.copy(), float(plate_conf), quality)

                if lat and not lat.first_usable_plate_monotonic:
                    lat.first_usable_plate_monotonic = current_monotonic
                    lat.first_usable_plate_pts = current_pts
                    
                last_ocr_submit[track_id] = frame_id


                ocr_candidates.append({
                    "track_id": track_id,
                    "frame_id": frame_id,
                    "crop":     crop,
                })
                
                # Phase G: Cache metadata for fusion
                pending_ocr_metadata[(frame_id, track_id)] = {
                    "quality_score": quality,
                    "detector_confidence": float(plate_conf),
                    "submitted_at": time.perf_counter()
                }

        plate_result_ms_total += (time.perf_counter() - _t_plate_res) * 1000.0

        # --------------------------------------------------------
        # SUBMIT OCR ASYNCHRONOUSLY (non-blocking, timed)
        # --------------------------------------------------------
        _t_ocr_sub = time.perf_counter()

        if ocr_candidates:
            
            ocr_worker.submit(ocr_candidates)
            ocr_submissions += len(ocr_candidates)
            for cand in ocr_candidates:
                lat = track_latencies.get(cand["track_id"])
                if lat and not lat.first_ocr_submit_monotonic:
                    lat.first_ocr_submit_monotonic = current_monotonic
                    lat.first_ocr_submit_pts = current_pts


        ocr_submit_ms_total += (time.perf_counter() - _t_ocr_sub) * 1000.0

        # --------------------------------------------------------
        # DRAW (timed — skipped in performance mode except for status)
        # --------------------------------------------------------
        _t_draw = time.perf_counter()

        if not args.performance_mode:
            for (track_id, vehicle_conf, vehicle_box) in tracks:
                x1, y1, x2, y2 = vehicle_box
                # Draw vehicle box in thick bright cyan/yellow
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 4)

                result_for_track = current_frame_results.get(track_id)
                if result_for_track and result_for_track["text"]:
                    label = (
                        f"ID {track_id} | "
                        f"{result_for_track['text']} "
                        f"({result_for_track['confidence']:.2f})"
                    )
                else:
                    label = f"ID {track_id} | --"

                # Draw raw OCR text in bright green, large font
                cv2.putText(
                    frame, label, (x1, max(30, y1 - 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3, cv2.LINE_AA,
                )

                # Phase G: Render Track-Level Fused Plate separately
                fused = fused_results.get(track_id)
                if fused and fused.decision in ("CONFIRMED", "PROBABLE"):
                    fused_label = f"FUSED: {fused.fused_text} ({fused.confidence:.2f})"
                    # Draw fused text in bright magenta/pink, very large font
                    cv2.putText(
                        frame, fused_label, (x1, max(70, y1 + 35)),
                        cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 0, 255), 3, cv2.LINE_AA,
                    )

        drawing_display_ms_total += (time.perf_counter() - _t_draw) * 1000.0

        # --------------------------------------------------------
        # OTHER LOOP OVERHEAD (timed)
        # --------------------------------------------------------
        _t_other = time.perf_counter()

        elapsed = time.perf_counter() - start_time

        processing_fps = processed / elapsed if elapsed > 0 else 0.0

        frame_latency_ms = (time.perf_counter() - frame_start) * 1000.0

        # Optional output video — disabled in performance mode
        if args.output and not args.performance_mode:
            if output_writer is None:
                height, width = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                output_writer = cv2.VideoWriter(
                    args.output, fourcc, args.output_fps, (width, height)
                )
            output_writer.write(frame)

        # Periodic annotated preview save (works in WSL — no display needed)
        # Saves outputs/preview_latest.jpg every 10 processed frames
        if not args.performance_mode:
            try:
                # Always encode for MJPEG stream
                ret, jpeg_buf = cv2.imencode('.jpg', frame)
                if ret:
                    MJPEGStreamHandler.global_jpeg_buffer = jpeg_buf.tobytes()
                    
                # Save to disk every 10 frames
                if processed % 10 == 0:
                    prev_path = PROJECT_ROOT / "outputs" / "preview_latest.jpg"
                    prev_path.parent.mkdir(parents=True, exist_ok=True)
                    if ret:
                        with open(prev_path, "wb") as f:
                            f.write(MJPEGStreamHandler.global_jpeg_buffer)
            except Exception:
                pass

        # Live display — only attempt if DISPLAY env var set (not in WSL headless)
        if args.show and not args.performance_mode and os.environ.get("DISPLAY"):
            try:
                cv2.imshow("LIVE ANPR V2", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            except Exception:
                pass  # Silently skip if no display available

        # Performance-mode 30-second stop
        if args.performance_mode and elapsed > 30.0:
            print("Performance mode 30s limit reached.", flush=True)
            other_loop_ms_total += (time.perf_counter() - _t_other) * 1000.0
            total_frame_wall_ms_total += (time.perf_counter() - _t_loop_start) * 1000.0
            break

        other_loop_ms_total += (time.perf_counter() - _t_other) * 1000.0
        total_frame_wall_ms_total += (time.perf_counter() - _t_loop_start) * 1000.0

        # --------------------------------------------------------
        # STATUS LINE
        # --------------------------------------------------------
        if frames_since_report >= args.status_every:
            avg_div = max(1, processed)
            avg_age = (sum(frame_ages) / len(frame_ages)) if frame_ages else 0.0
            print(
                f"\rFrame {frame_id} | proc {processing_fps:.2f} fps | cap {capture.capture_fps:.1f} fps | "
                f"age_avg {avg_age:.0f}ms | "
                f"veh {vehicle_track_ms_total/avg_div:.0f}ms | "
                f"plate {plate_predict_ms_total/avg_div:.0f}ms | "
                f"wall {total_frame_wall_ms_total/avg_div:.0f}ms | "
                f"tracks {active_tracks} | "
                f"stale_drop {capture.frames_dropped_stale}",
                end="",
                flush=True,
            )
            frames_since_report = 0

    # ============================================================
    # CLEANUP
    # ============================================================

    capture.stop()
    ocr_worker.stop()
    ocr_client.close()

    if output_writer:
        output_writer.release()

    if csv_file:
        csv_file.close()

    cv2.destroyAllWindows()

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.perf_counter() - start_time
    processing_fps = processed / elapsed if elapsed > 0 else 0.0
    rt_ratio = processing_fps / args.input_fps if args.input_fps > 0 else 0.0

    max_vram = 0.0
    if torch.cuda.is_available():
        max_vram = torch.cuda.max_memory_allocated() / (1024 ** 3)

    avg_div = max(1, processed)

    # Compute frame-age percentiles
    import statistics as _stats
    if frame_ages:
        sorted_ages = sorted(frame_ages)
        n = len(sorted_ages)
        avg_age_ms = sum(sorted_ages) / n
        p95_age_ms = sorted_ages[min(int(0.95 * n), n - 1)]
        p99_age_ms = sorted_ages[min(int(0.99 * n), n - 1)]
        max_age_ms = sorted_ages[-1]
    else:
        avg_age_ms = p95_age_ms = p99_age_ms = max_age_ms = 0.0

    print()
    print()
    print("=" * 70)
    print("REALTIME ANPR — Phase I: Low-Latency Live CCTV Report")
    print("=" * 70)
    print(f"Source type        : {'FILE' if not str(args.source).startswith(('rtsp','http','0','1','2')) else 'LIVE/RTSP'}")
    print(f"Source             : {args.source}")
    print(f"Input FPS (arg)    : {args.input_fps:.1f}")
    print(f"Capture FPS (meas) : {capture.capture_fps:.2f}")
    print(f"Processing FPS     : {processing_fps:.2f}")
    print(f"Realtime ratio     : {rt_ratio:.2f}x")
    print()
    print("--- CAPTURE Telemetry ---")
    print(f"  Frames received        : {capture.frames_received}")
    print(f"  Frames decoded         : {capture.frames_decoded}")
    print(f"  Stale frames dropped   : {capture.frames_dropped_stale}")
    print(f"  Reconnects             : {capture.reconnect_count}")
    print()
    print("--- FRAME AGE (application-side freshness) ---")
    print("  NOTE: Measured as time from capture thread publish to")
    print("        inference thread processing. NOT camera sensor time.")
    print(f"  Frames measured        : {len(frame_ages)}")
    print(f"  Average frame age      : {avg_age_ms:.1f} ms")
    print(f"  p95 frame age          : {p95_age_ms:.1f} ms")
    print(f"  p99 frame age          : {p99_age_ms:.1f} ms")
    print(f"  Max frame age          : {max_age_ms:.1f} ms")
    print()
    print("--- VEHICLE Stage ---")
    print(f"{'Component':<30} {'Average ms':>12}")
    print("-" * 44)
    print(f"{'capture read':<30} {capture_read_ms_total/avg_div:>12.2f}")
    print(f"{'capture sleep/wait':<30} {capture_sleep_ms_total/avg_div:>12.2f}")
    print(f"{'OCR check':<30} {ocr_check_ms_total/avg_div:>12.2f}")
    print(f"{'vehicle tracking':<30} {vehicle_track_ms_total/avg_div:>12.2f}")
    print(f"{'vehicle result processing':<30} {vehicle_result_ms_total/avg_div:>12.2f}")
    print(f"{'plate batch construction':<30} {plate_batch_build_ms_total/avg_div:>12.2f}")
    print(f"{'plate prediction':<30} {plate_predict_ms_total/avg_div:>12.2f}")
    print(f"{'plate result processing':<30} {plate_result_ms_total/avg_div:>12.2f}")
    print(f"{'OCR submission':<30} {ocr_submit_ms_total/avg_div:>12.2f}")
    print(f"{'drawing/display':<30} {drawing_display_ms_total/avg_div:>12.2f}")
    print(f"{'other':<30} {other_loop_ms_total/avg_div:>12.2f}")
    print(f"{'TOTAL WALL TIME':<30} {total_frame_wall_ms_total/avg_div:>12.2f}")
    print()
    if vehicle_predict_calls > 0:
        print(f"  Vehicle preprocess ms  : {vehicle_preprocess_ms_total/vehicle_predict_calls:.2f}")
        print(f"  Vehicle inference ms   : {vehicle_inference_ms_total/vehicle_predict_calls:.2f}")
        print(f"  Vehicle postprocess ms : {vehicle_postprocess_ms_total/vehicle_predict_calls:.2f}")
        print(f"  Vehicle total wall ms  : {vehicle_total_ms_total/vehicle_predict_calls:.2f}")
    print()
    print("--- PLATE Stage ---")
    print(f"  Plate predict calls    : {plate_predict_calls}")
    print(f"  Plate images submitted : {plate_inference_images}")
    if plate_predict_calls > 0:
        print(f"  Avg plate batch size   : {plate_inference_images/plate_predict_calls:.2f}")
        print(f"  Plate pre-proc ms/call : {plate_preprocess_ms/plate_predict_calls:.2f}")
        print(f"  Plate infer ms/call    : {plate_infer_ms/plate_predict_calls:.2f}")
        print(f"  Plate post-proc ms/call: {plate_postprocess_ms/plate_predict_calls:.2f}")
        print(f"  Plate total wall ms    : {plate_predict_ms_total/avg_div:.2f}")
    print()
    print("--- Plate Eligibility ---")
    print(f"  Tracks considered      : {plate_tracks_considered}")
    print(f"  Tracks submitted       : {plate_tracks_submitted}")
    print(f"  Skipped (cooldown)     : {plate_tracks_skipped_cooldown}")
    print(f"  Skipped (size)         : {plate_tracks_skipped_size}")
    print()
    print("--- OCR ---")
    if ocr_results > 0:
        print(f"  OCR round-trip ms      : {ocr_round_trip_total/ocr_results:.1f}")
    print(f"  OCR submitted          : {ocr_submissions}")
    print(f"  OCR completed          : {ocr_results}")
    print(f"  OCR dropped            : {ocr_jobs_dropped}")
    print(f"  Orphan OCR results     : {orphan_ocr_results}")
    print()
    print("--- Temporal Fusion ---")
    t = get_telemetry()
    print(f"  Total observations     : {t.total_observations_processed}")
    print(f"  Fusion attempts        : {t.fusion_attempts}")
    print(f"  CONFIRMED count        : {t.confirmed_count}")
    print(f"  PROBABLE count         : {t.probable_count}")
    print(f"  UNREADABLE count       : {t.unreadable_count}")
    print(f"  Tracks with 1 obs      : {t.tracks_with_1_observation}")
    print(f"  Tracks with 2+ obs     : {t.tracks_with_2plus_observations}")
    print(f"  Max obs (any track)    : {t.max_observations_seen_for_any_track}")
    print(f"  Avg quality score      : {t.average_quality_score:.3f}")
    print(f"  Avg fusion confidence  : {t.average_fusion_confidence:.3f}")
    print()
    print("--- Tracking ---")
    print(f"  Frames processed       : {processed}")
    print(f"  Active tracks (final)  : {active_tracks}")
    print(f"  Track creations total  : {track_creations}")
    print(f"  ID disappearances      : {track_id_disappearances}")
    print()

    print("--- TRUE LOW LATENCY METRICS ---")
    first_ocr_lats = [ (l.first_ocr_result_pts - l.first_seen_pts) for l in completed_track_metrics if l.first_ocr_result_pts and l.first_seen_pts ]
    confirmed_lats = [ (l.confirmed_pts - l.first_seen_pts) for l in completed_track_metrics if l.confirmed_pts and l.first_seen_pts ]
    lifetimes = [ (l.track_end_pts - l.first_seen_pts) for l in completed_track_metrics if l.track_end_pts and l.first_seen_pts ]
    
    def p50(lst): return np.percentile(lst, 50) if lst else 0
    def p95(lst): return np.percentile(lst, 95) if lst else 0

    print(f"  Tracks observed : {len(completed_track_metrics)}")
    print(f"  Tracks with plate detections : {len([l for l in completed_track_metrics if l.first_plate_detection_pts])}")
    print(f"  Tracks with OCR : {len(first_ocr_lats)}")
    print(f"  Tracks confirmed : {len(confirmed_lats)}")
    print(f"  Median first OCR latency : {p50(first_ocr_lats):.1f} ms")
    print(f"  P95 first OCR latency : {p95(first_ocr_lats):.1f} ms")
    print(f"  Median time-to-confirmed : {p50(confirmed_lats):.1f} ms")
    print(f"  P95 time-to-confirmed : {p95(confirmed_lats):.1f} ms")
    print(f"  Median track lifetime : {p50(lifetimes):.1f} ms")
    print(f"  P95 track lifetime : {p95(lifetimes):.1f} ms")
    print(f"  OCR duplicate skips : {ocr_duplicate_skips}")
    print(f"  OCR unique submissions : {ocr_unique_submissions}")
    print()
    print(f"GPU VRAM used          : {max_vram:.2f} GB")
    print("=" * 70)
    print()
    print("BOTTLENECK ASSESSMENT:")
    bottleneck = "vehicle inference" if vehicle_predict_calls > 0 and (vehicle_total_ms_total/vehicle_predict_calls) > 50 else "unknown"
    print(f"  Current bottleneck     : {bottleneck}")
    print(f"  Average vehicle ms     : {vehicle_total_ms_total/max(1,vehicle_predict_calls):.1f}")
    print(f"  Average plate ms       : {plate_time_total/max(1,plate_predict_calls) * 1000:.1f}" if plate_predict_calls > 0 else "  Average plate ms       : 0.0")
    print("=" * 70)


# ================================================================
# ARGUMENT PARSING
# ================================================================

def parse_args():

    parser = argparse.ArgumentParser(description="Realtime ANPR V2 — Phase F")

    parser.add_argument("--source", required=True,
                        help="Video path, webcam index, or RTSP URL.")
    parser.add_argument("--vehicle-model", default=str(DEFAULT_VEHICLE_MODEL))
    parser.add_argument("--plate-model",   default=str(DEFAULT_PLATE_MODEL))
    parser.add_argument("--vehicle-conf",  type=float, default=0.25)
    parser.add_argument("--plate-conf",    type=float, default=0.20)
    parser.add_argument("--vehicle-imgsz", type=int,   default=640)
    parser.add_argument("--plate-imgsz",   type=int,   default=416)

    # Phase F: renamed from --redetect-every
    parser.add_argument("--plate-cadence",       type=int, default=2,
                        help="Run plate YOLO every N processed frames.")
    parser.add_argument("--plate-track-cooldown", type=int, default=0,
                        help="Minimum frames between plate observations per track.")
    parser.add_argument("--min-vehicle-width",   type=int, default=30,
                        help="Skip plate YOLO for vehicles narrower than this px.")
    parser.add_argument("--min-vehicle-height",  type=int, default=20,
                        help="Skip plate YOLO for vehicles shorter than this px.")

    parser.add_argument("--ocr-spacing",    type=int,   default=4)
    parser.add_argument("--ocr-batch-size", type=int,   default=8)
    parser.add_argument("--plate-batch-size", type=int, default=8)
    parser.add_argument("--min-plate-width", type=int,  default=20)
    parser.add_argument("--min-quality",    type=float, default=0.10)
    parser.add_argument("--output",         default="")
    parser.add_argument("--csv",            default="")
    parser.add_argument("--output-fps",     type=float, default=30.0)
    parser.add_argument("--input-fps",      type=float, default=30.0)
    parser.add_argument("--status-every",   type=int,   default=5)
    parser.add_argument("--show",           action="store_true")
    parser.add_argument("--debug",          action="store_true",
                        help="Print per-frame RAW/FILTERED/TRACK lines (slow, for diagnosis only).")
    parser.add_argument("--rotate",          default="cw", choices=["cw", "ccw", "none"],
                        help="Rotate portrait frames: cw=clockwise, ccw=counterclockwise, none=off.")
    parser.add_argument("--performance-mode", action="store_true",
                        help="Disable display, video encoding, CSV writes.")

    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
