"""
YOLO + ByteTrack Detection Diagnostic
Prints per-frame: raw detections, class filter, tracker input/output
Runs on the first N frames of a video source.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO

# ================================================================
# CONFIG
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VEHICLE_MODEL = PROJECT_ROOT / "yolov8n.pt"
SOURCE        = str(PROJECT_ROOT / "data" / "test" / "indian_test.mp4")
IMGSZ         = 512
CONF          = 0.25
VEHICLE_CLASSES = [2, 3, 5, 7]   # car, motorbike, bus, truck
MAX_FRAMES    = 20                 # how many frames to trace

# COCO class names (subset we care about + unknowns)
COCO_NAMES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
    4: "airplane", 5: "bus", 6: "train", 7: "truck", 8: "boat",
    9: "traffic light", 10: "fire hydrant", 11: "stop sign",
    12: "parking meter",
}

# ================================================================
# SETUP
# ================================================================
use_gpu = torch.cuda.is_available()
device  = 0 if use_gpu else "cpu"

print("=" * 70)
print("YOLO + BYTETRACK DETECTION DIAGNOSTIC")
print("=" * 70)
print(f"  Source  : {SOURCE}")
print(f"  Device  : {'cuda:0 (' + torch.cuda.get_device_name(0) + ')' if use_gpu else 'CPU'}")
print(f"  imgsz   : {IMGSZ}")
print(f"  conf    : {CONF}")
print(f"  vehicle classes (COCO IDs): {VEHICLE_CLASSES}")
print(f"  Frames to trace: {MAX_FRAMES}")
print("=" * 70)

model = YOLO(VEHICLE_MODEL)
if use_gpu:
    model.model.half()
    print(f"  Model dtype: {next(model.model.parameters()).dtype}")

# Single warmup
dummy = np.zeros((640, 640, 3), dtype=np.uint8)
model.predict(dummy, imgsz=IMGSZ, device=device, verbose=False)
print("  Warmup OK\n")

# ================================================================
# OPEN VIDEO
# ================================================================
cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    print(f"ERROR: cannot open {SOURCE}")
    sys.exit(1)

fps   = cap.get(cv2.CAP_PROP_FPS)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"  Video: {total} frames @ {fps:.2f} fps\n")

# ================================================================
# PER-FRAME TRACE
# ================================================================
frame_idx = 0

while frame_idx < MAX_FRAMES:
    ok, frame = cap.read()
    if not ok:
        print("  End of video or read failure.")
        break

    frame_idx += 1
    print(f"\n{'─'*70}")
    print(f"  FRAME {frame_idx:03d}  (shape {frame.shape[1]}×{frame.shape[0]})")
    print(f"{'─'*70}")

    # ── 1. Run model.track() ────────────────────────────────────
    results = model.track(
        frame,
        imgsz=IMGSZ,
        device=device,
        persist=True,
        tracker="bytetrack.yaml",
        conf=CONF,
        verbose=False,
    )

    result = results[0]
    boxes = result.boxes

    # ── 2. RAW YOLO detections (all classes) ────────────────────
    print(f"\n  [RAW YOLO] — all classes (before vehicle filter)")
    if boxes is None or len(boxes) == 0:
        print("    (no raw detections)")
    else:
        raw_xyxy  = boxes.xyxy.cpu().numpy()
        raw_conf  = boxes.conf.cpu().numpy()
        raw_cls   = boxes.cls.cpu().numpy().astype(int)
        raw_ids   = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else [None] * len(raw_cls)

        print(f"  {'#':<4} {'cls_id':<8} {'class_name':<14} {'conf':<8} {'track_id':<12} {'x1':>6} {'y1':>6} {'x2':>6} {'y2':>6}")
        print(f"  {'─'*78}")
        for i, (box, conf, cls, tid) in enumerate(zip(raw_xyxy, raw_conf, raw_cls, raw_ids)):
            x1, y1, x2, y2 = map(int, box)
            name = COCO_NAMES.get(cls, f"cls_{cls}")
            tid_str = str(tid) if tid is not None else "None"
            print(f"  {i:<4} {cls:<8} {name:<14} {conf:<8.3f} {tid_str:<12} {x1:>6} {y1:>6} {x2:>6} {y2:>6}")

    # ── 3. AFTER VEHICLE CLASS FILTER ──────────────────────────
    print(f"\n  [VEHICLE FILTER] — keeping classes {VEHICLE_CLASSES}")
    if boxes is None or len(boxes) == 0:
        print("    (nothing to filter)")
        filtered = []
    else:
        raw_cls_arr = boxes.cls.cpu().numpy().astype(int)
        keep_mask   = np.isin(raw_cls_arr, VEHICLE_CLASSES)
        filtered_xyxy = raw_xyxy[keep_mask]
        filtered_conf = raw_conf[keep_mask]
        filtered_cls  = raw_cls_arr[keep_mask]
        filtered_ids  = np.array([
            raw_ids[i] for i in range(len(raw_cls_arr)) if keep_mask[i]
        ])

        if len(filtered_xyxy) == 0:
            print("    (no vehicles after filter)")
        else:
            print(f"  {'#':<4} {'cls_id':<8} {'class_name':<14} {'conf':<8} {'track_id':<12} {'x1':>6} {'y1':>6} {'x2':>6} {'y2':>6}")
            print(f"  {'─'*78}")
            for i, (box, conf, cls, tid) in enumerate(zip(filtered_xyxy, filtered_conf, filtered_cls, filtered_ids)):
                x1, y1, x2, y2 = map(int, box)
                name = COCO_NAMES.get(cls, f"cls_{cls}")
                tid_str = str(tid) if tid is not None else "None"
                print(f"  {i:<4} {cls:<8} {name:<14} {conf:<8.3f} {tid_str:<12} {x1:>6} {y1:>6} {x2:>6} {y2:>6}")

    # ── 4. TRACKER INTERNAL STATE (read-only) ──────────────────
    print(f"\n  [TRACKER STATE] — ByteTrack internal read-only snapshot")
    try:
        tracker = model.predictor.trackers[0]
        tracked  = getattr(tracker, "tracked_stracks",  [])
        lost     = getattr(tracker, "lost_stracks",     [])
        removed  = getattr(tracker, "removed_stracks",  [])

        print(f"    active tracked : {len(tracked)}")
        print(f"    lost (pending) : {len(lost)}")
        print(f"    removed (done) : {len(removed)}")

        if tracked:
            print(f"\n    Active tracks:")
            print(f"    {'track_id':<12} {'score':<8} {'state':<10}")
            print(f"    {'─'*32}")
            for s in tracked:
                score = getattr(s, "score", "?")
                state = getattr(s, "state", "?")
                print(f"    {s.track_id:<12} {score!s:<8} {state!s:<10}")
        if lost:
            print(f"\n    Lost (will be removed after max_time_lost):")
            for s in lost:
                print(f"    track_id={s.track_id}  score={getattr(s, 'score', '?'):.3f}")

    except AttributeError as e:
        print(f"    Could not access tracker internals: {e}")

cap.release()

print(f"\n{'='*70}")
print(f"Diagnostic complete. {frame_idx} frames traced.")
print(f"{'='*70}")
