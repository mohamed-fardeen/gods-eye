"""
offline_pipeline.py — Batch ANPR observation extractor for evaluation.

Processes a video file frame-by-frame (no reconnect loop, no frame drop).
Outputs a rich observations CSV with all fields required by the ablation:
    frame_id, track_id, raw_text, ocr_confidence, detector_confidence,
    quality_score, timestamp

Does NOT modify models, fusion, or OCR server configuration.

Usage:
    PYTHONPATH=. python scripts/offline_pipeline.py \\
        --source data/test/indian_test.mp4 \\
        --csv outputs/indian_observations.csv \\
        --vehicle-imgsz 512 --plate-cadence 12
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import socket
import struct
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VEHICLE_MODEL = PROJECT_ROOT / "yolov8n.pt"
DEFAULT_PLATE_MODEL   = PROJECT_ROOT / "models" / "plate_detector" / "weights" / "best.pt"
OCR_HOST = "127.0.0.1"
OCR_PORT = 8765

VEHICLE_CLASSES = [2, 3, 5, 7]


# ──────────────────────────────────────────────────────────────
# Quality scoring (same formula as realtime_anpr.py)
# ──────────────────────────────────────────────────────────────

def quality_score(crop: np.ndarray) -> float:
    if crop is None or crop.size == 0:
        return 0.0
    h, w = crop.shape[:2]
    gray  = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    sharp = min(float(cv2.Laplacian(gray, cv2.CV_64F).var()) / 400.0, 1.0)
    size  = min((w * h) / 8000.0, 1.0)
    aspect = w / max(h, 1)
    geometry = 1.0 if 1.5 <= aspect <= 8.0 else 0.0
    return float(0.55 * sharp + 0.30 * size + 0.15 * geometry)


# ──────────────────────────────────────────────────────────────
# JSON+hex framed protocol helpers (same as ocr_worker.py)
# ──────────────────────────────────────────────────────────────

def _send_message(s: socket.socket, msg: dict) -> None:
    payload = json.dumps(msg, separators=(",", ":")).encode("utf-8")
    s.sendall(struct.pack("!I", len(payload)) + payload)


def _recv_message(s: socket.socket) -> dict:
    raw_len = _recv_exact(s, 4)
    if raw_len is None:
        return {}
    size = struct.unpack("!I", raw_len)[0]
    raw_body = _recv_exact(s, size)
    if raw_body is None:
        return {}
    return json.loads(raw_body.decode("utf-8"))


# ──────────────────────────────────────────────────────────────
# Blocking OCR call — uses the same JSON/hex protocol as OCRClient
# ──────────────────────────────────────────────────────────────

_ocr_request_counter = 0

def ocr_request(crop: np.ndarray, host=OCR_HOST, port=OCR_PORT, timeout=5.0):
    """Send a plate crop to the PaddleOCR server; return (text, confidence)."""
    global _ocr_request_counter
    ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return "", 0.0
    _ocr_request_counter += 1
    message = {
        "request_id": _ocr_request_counter,
        "items": [{
            "track_id": 0,
            "frame_id": 0,
            "image_hex": buf.tobytes().hex(),
        }]
    }
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            _send_message(s, message)
            resp = _recv_message(s)
            results = resp.get("results", [])
            if not results:
                return "", 0.0
            best = max(results, key=lambda r: r.get("confidence", 0.0))
            return best.get("text", ""), float(best.get("confidence", 0.0))
    except Exception:
        return "", 0.0


def _recv_exact(s: socket.socket, n: int):
    buf = b""
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


# ──────────────────────────────────────────────────────────────
# Letterbox helpers (same as realtime_anpr.py)
# ──────────────────────────────────────────────────────────────

def letterbox(img, new_shape=(416, 416), color=(114, 114, 114)):
    shape = img.shape[:2]
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw = (new_shape[1] - new_unpad[0]) / 2
    dh = (new_shape[0] - new_unpad[1]) / 2
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right,
                              cv2.BORDER_CONSTANT, value=color)
    return img, r, (dw, dh)


def scale_boxes(boxes, r, pad):
    dw, dh = pad
    boxes[:, [0, 2]] -= dw
    boxes[:, [1, 3]] -= dh
    boxes /= r
    return boxes


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def run(args):
    use_gpu  = torch.cuda.is_available()
    device   = 0 if use_gpu else "cpu"
    use_half = use_gpu

    print("=" * 60)
    print("OFFLINE ANPR OBSERVATION EXTRACTOR")
    print("=" * 60)
    print(f"Source         : {args.source}")
    print(f"Vehicle imgsz  : {args.vehicle_imgsz}")
    print(f"Plate cadence  : {args.plate_cadence}")
    print(f"Min quality    : {args.min_quality}")
    print(f"Output CSV     : {args.csv}")
    print(f"Output Video   : {args.output}")
    print("=" * 60)

    # Load models
    vehicle_model = YOLO(str(DEFAULT_VEHICLE_MODEL))
    plate_model   = YOLO(str(DEFAULT_PLATE_MODEL))
    print("Models loaded.")

    # Open video (single sequential read — no reconnect loop)
    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        print(f"ERROR: Cannot open {args.source}")
        return
    fps        = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video: {total_frames} frames @ {fps:.2f} FPS")

    # Output CSV
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    out_file   = open(args.csv, "w", newline="", encoding="utf-8")
    out_writer = csv.writer(out_file)
    out_writer.writerow([
        "frame_id", "timestamp", "track_id",
        "raw_text", "ocr_confidence",
        "quality_score", "detector_confidence",
    ])

    video_writer = None
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(args.output, fourcc, fps, (w, h))

    # Tracker state (track_id assignment from ByteTrack via YOLO track)
    last_plate_run = {}   # track_id → last frame plate YOLO ran
    obs_count      = 0
    t_start        = time.perf_counter()

    frame_id = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break   # end of file — do NOT reconnect

        timestamp = frame_id / fps

        # ── Vehicle detection + tracking ──────────────────────
        v_results = vehicle_model.track(
            frame,
            imgsz=args.vehicle_imgsz,
            persist=True,
            tracker="bytetrack.yaml",
            device=device,
            half=use_half,
            verbose=False,
            classes=VEHICLE_CLASSES,
            conf=0.3,
        )

        if v_results and v_results[0].boxes is not None:
            boxes  = v_results[0].boxes
            xyxys  = boxes.xyxy.cpu().numpy()
            confs  = boxes.conf.cpu().numpy()
            t_ids  = boxes.id
            track_ids = t_ids.cpu().numpy().astype(int) if t_ids is not None else []

            for i, track_id in enumerate(track_ids):
                track_id = int(track_id)
                x1, y1, x2, y2 = [int(c) for c in xyxys[i]]
                
                # Draw vehicle box and track ID
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

                # ── Plate cadence gate ──────────────────────
                last = last_plate_run.get(track_id, -9999)
                if (frame_id - last) < args.plate_cadence:
                    continue
                last_plate_run[track_id] = frame_id

                # ── Extract vehicle crop ─────────────────────
                x1, y1 = max(x1, 0), max(y1, 0)
                x2, y2 = min(x2, frame.shape[1]), min(y2, frame.shape[0])
                vehicle_crop = frame[y1:y2, x1:x2]
                if vehicle_crop.size == 0:
                    continue

                # ── Plate detection ───────────────────────────
                lb, r, pad = letterbox(vehicle_crop,
                                        new_shape=(args.plate_imgsz, args.plate_imgsz))
                p_results = plate_model(
                    lb,
                    imgsz=args.plate_imgsz,
                    device=device,
                    half=use_half,
                    verbose=False,
                    conf=0.25,
                )
                if not p_results or p_results[0].boxes is None:
                    continue

                p_boxes = p_results[0].boxes.xyxy.cpu().numpy()
                p_confs = p_results[0].boxes.conf.cpu().numpy()
                if len(p_boxes) == 0:
                    continue

                # Scale back to vehicle crop coordinates
                p_boxes_scaled = scale_boxes(p_boxes.copy(), r, pad)
                # Pick highest-confidence plate
                best_p = int(np.argmax(p_confs))
                px1, py1, px2, py2 = [int(c) for c in p_boxes_scaled[best_p]]
                px1, py1 = max(px1, 0), max(py1, 0)
                px2, py2 = min(px2, vehicle_crop.shape[1]), min(py2, vehicle_crop.shape[0])
                plate_crop = vehicle_crop[py1:py2, px1:px2]
                if plate_crop.size == 0:
                    continue

                det_conf = float(p_confs[best_p])

                # ── Quality score ─────────────────────────────
                q = quality_score(plate_crop)
                if q < args.min_quality:
                    continue

                # ── OCR ──────────────────────────────────────
                text, ocr_conf = ocr_request(plate_crop)

                # Write row regardless of OCR success (empty text = no read)
                out_writer.writerow([
                    frame_id, f"{timestamp:.3f}", track_id,
                    text, f"{ocr_conf:.6f}",
                    f"{q:.6f}", f"{det_conf:.6f}",
                ])
                obs_count += 1
                
                # Draw plate bounding box and text
                cv2.rectangle(frame, (px1+x1, py1+y1), (px2+x1, py2+y1), (0, 0, 255), 2)
                if text:
                    cv2.putText(frame, f"{text} ({ocr_conf:.2f})", (px1+x1, py1+y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if video_writer:
            video_writer.write(frame)
            
        frame_id += 1

        if frame_id % 100 == 0:
            elapsed = time.perf_counter() - t_start
            pct = frame_id / max(total_frames, 1) * 100
            print(f"\r[{pct:5.1f}%] frame {frame_id}/{total_frames} | "
                  f"{frame_id/elapsed:.2f} fps | obs {obs_count}", end="", flush=True)

    cap.release()
    out_file.close()
    if video_writer:
        video_writer.release()

    elapsed = time.perf_counter() - t_start
    print(f"\nDone. {frame_id} frames processed in {elapsed:.1f}s "
          f"({frame_id/elapsed:.2f} fps). {obs_count} observations written to {args.csv}.")


def parse_args():
    ap = argparse.ArgumentParser(description="Offline ANPR observation extractor")
    ap.add_argument("--source",          required=True)
    ap.add_argument("--output",          default="")
    ap.add_argument("--csv",             default="outputs/indian_observations.csv")
    ap.add_argument("--vehicle-imgsz",   type=int,   default=512)
    ap.add_argument("--plate-imgsz",     type=int,   default=416)
    ap.add_argument("--plate-cadence",   type=int,   default=12)
    ap.add_argument("--min-quality",     type=float, default=0.1)
    return ap.parse_args()


if __name__ == "__main__":
    run(parse_args())
