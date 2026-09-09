"""
Phase I-B: GPU Execution Verification + Microbenchmark
Isolated diagnostic — no capture, no OCR, no plate detection.
"""
from __future__ import annotations

import time
import subprocess
from pathlib import Path

import numpy as np
import torch
from ultralytics import YOLO

# ================================================================
# CONFIG
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VEHICLE_MODEL = PROJECT_ROOT / "yolov8n.pt"
VEHICLE_IMGSZ = 512
VEHICLE_CLASSES = [2, 3, 5, 7]
VEHICLE_CONF = 0.25
WARMUP = 100
MEASURED = 200

# ================================================================
# SECTION 1: CUDA STATUS
# ================================================================

print("=" * 70)
print("SECTION 1 — CUDA ENVIRONMENT")
print("=" * 70)
cuda_avail = torch.cuda.is_available()
print(f"  torch.cuda.is_available() : {cuda_avail}")
if cuda_avail:
    print(f"  torch.cuda.device_count() : {torch.cuda.device_count()}")
    print(f"  torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"  Total VRAM                : {props.total_memory / 1024**3:.2f} GB")
    print(f"  Compute capability        : {props.major}.{props.minor}")
else:
    print("  *** CUDA NOT AVAILABLE — all inference will be on CPU ***")
print()

# ================================================================
# SECTION 2: LOAD VEHICLE MODEL
# ================================================================

print("=" * 70)
print("SECTION 2 — MODEL LOAD + DEVICE/DTYPE AUDIT")
print("=" * 70)

use_gpu = cuda_avail
device = 0 if use_gpu else "cpu"

# Use the new Ultralytics API — 'half' is deprecated, use quantize instead
vehicle_model = YOLO(VEHICLE_MODEL)

# Move to device explicitly
if use_gpu:
    vehicle_model.model.to(device)

# Check actual parameter device and dtype BEFORE any inference
param = next(vehicle_model.model.parameters())
print(f"  Model parameter device     : {param.device}")
print(f"  Model parameter dtype      : {param.dtype}")
print(f"  Requested device           : {device}")

# Check if the model is in FP16
is_fp16 = param.dtype == torch.float16
print(f"  Actually FP16?             : {is_fp16}")
if not is_fp16:
    print("  NOTE: Model is FP32. 'half' deprecation warning is from Ultralytics")
    print("        argument parsing, not necessarily from actual FP32 execution.")
print()

# ================================================================
# SECTION 3: FP16 API CHECK
# ================================================================

print("=" * 70)
print("SECTION 3 — FP16 / QUANTIZE API")
print("=" * 70)

# The correct modern API is model.model.half() or passing quantize=True
# Let's check what Ultralytics currently recommends
try:
    import inspect
    track_sig = inspect.signature(vehicle_model.track)
    predict_sig = inspect.signature(vehicle_model.predict)
    print(f"  track() accepts 'half'?    : {'half' in track_sig.parameters}")
    print(f"  track() accepts 'quantize'?: {'quantize' in track_sig.parameters}")
    print(f"  predict() accepts 'half'?  : {'half' in predict_sig.parameters}")
    print(f"  predict() accepts 'quantize'?: {'quantize' in predict_sig.parameters}")
except Exception as e:
    print(f"  Could not inspect signature: {e}")
print()

# ================================================================
# SECTION 4: CUDA SYNC AUDIT
# ================================================================

print("=" * 70)
print("SECTION 4 — CUDA SYNCHRONIZE AUDIT")
print("=" * 70)
import re
realtime_path = PROJECT_ROOT / "app" / "realtime" / "realtime_anpr.py"
sync_lines = []
with open(realtime_path) as f:
    for i, line in enumerate(f, 1):
        if "cuda.synchronize" in line:
            sync_lines.append((i, line.rstrip()))
print(f"  cuda.synchronize() calls in realtime_anpr.py: {len(sync_lines)}")
for lineno, content in sync_lines:
    print(f"    Line {lineno:4d}: {content.strip()}")
print()

# ================================================================
# SECTION 5: WARMUP
# ================================================================

print("=" * 70)
print("SECTION 5 — WARMUP (100 iterations, single 1280×720 frame)")
print("=" * 70)

dummy_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

print("  Running warmup...")
for i in range(WARMUP):
    _ = vehicle_model.predict(
        dummy_frame,
        imgsz=VEHICLE_IMGSZ,
        device=device,
        verbose=False,
        classes=VEHICLE_CLASSES,
        conf=VEHICLE_CONF,
    )
    if i == 0:
        r = _[0]
        print(f"  First warmup result device : {r.boxes.xyxy.device if r.boxes and len(r.boxes) else 'no detections (check input)'}")

if use_gpu:
    torch.cuda.synchronize()
print("  Warmup complete.")
print()

# ================================================================
# SECTION 6: RAW YOLO MICROBENCHMARK (predict, no tracker)
# ================================================================

print("=" * 70)
print(f"SECTION 6 — RAW YOLO MICROBENCHMARK ({MEASURED} frames, imgsz={VEHICLE_IMGSZ})")
print("=" * 70)
print("  (No tracker, no plate, no OCR, no video capture)")
print()

wall_times = []
ultralytics_preprocess = []
ultralytics_inference  = []
ultralytics_postprocess = []

for i in range(MEASURED):
    t0 = time.perf_counter()
    results = vehicle_model.predict(
        dummy_frame,
        imgsz=VEHICLE_IMGSZ,
        device=device,
        verbose=False,
        classes=VEHICLE_CLASSES,
        conf=VEHICLE_CONF,
    )
    if use_gpu:
        torch.cuda.synchronize()
    t1 = time.perf_counter()
    wall_times.append((t1 - t0) * 1000.0)

    r = results[0]
    if hasattr(r, "speed"):
        ultralytics_preprocess.append(r.speed.get("preprocess", 0.0))
        ultralytics_inference.append(r.speed.get("inference", 0.0))
        ultralytics_postprocess.append(r.speed.get("postprocess", 0.0))

wall_times.sort()
n = len(wall_times)
avg_wall = sum(wall_times) / n
p50_wall = wall_times[n // 2]
p95_wall = wall_times[int(0.95 * n)]
p99_wall = wall_times[int(0.99 * n)]
min_wall = wall_times[0]

print(f"  Wall clock (ms):")
print(f"    Min    : {min_wall:.2f}")
print(f"    Avg    : {avg_wall:.2f}")
print(f"    p50    : {p50_wall:.2f}")
print(f"    p95    : {p95_wall:.2f}")
print(f"    p99    : {p99_wall:.2f}")
print(f"    FPS    : {1000.0/avg_wall:.1f}")
print()

if ultralytics_inference:
    avg_pre  = sum(ultralytics_preprocess)  / len(ultralytics_preprocess)
    avg_inf  = sum(ultralytics_inference)   / len(ultralytics_inference)
    avg_post = sum(ultralytics_postprocess) / len(ultralytics_postprocess)
    print(f"  Ultralytics speed dict (ms, averaged):")
    print(f"    preprocess  : {avg_pre:.2f}")
    print(f"    inference   : {avg_inf:.2f}")
    print(f"    postprocess : {avg_post:.2f}")
    print(f"    sum         : {avg_pre + avg_inf + avg_post:.2f}")
    print(f"    unexplained : {avg_wall - (avg_pre + avg_inf + avg_post):.2f}  ← overhead")
print()

# ================================================================
# SECTION 7: YOLO + BYTETRACK BENCHMARK
# ================================================================

print("=" * 70)
print(f"SECTION 7 — YOLO + BYTETRACK ({MEASURED} frames)")
print("=" * 70)
print("  (Tracker only, no plate, no OCR, no capture)")
print()

track_wall_times = []
yolo_speed_pre  = []
yolo_speed_inf  = []
yolo_speed_post = []
tracker_times   = []

for i in range(MEASURED):
    t0 = time.perf_counter()
    results = vehicle_model.track(
        dummy_frame,
        imgsz=VEHICLE_IMGSZ,
        device=device,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False,
        classes=VEHICLE_CLASSES,
        conf=VEHICLE_CONF,
    )
    if use_gpu:
        torch.cuda.synchronize()
    t1 = time.perf_counter()
    track_wall_times.append((t1 - t0) * 1000.0)

    r = results[0]
    if hasattr(r, "speed"):
        yolo_speed_pre.append(r.speed.get("preprocess", 0.0))
        yolo_speed_inf.append(r.speed.get("inference", 0.0))
        yolo_speed_post.append(r.speed.get("postprocess", 0.0))

track_wall_times.sort()
n = len(track_wall_times)
avg_track  = sum(track_wall_times) / n
p50_track  = track_wall_times[n // 2]
p95_track  = track_wall_times[int(0.95 * n)]
min_track  = track_wall_times[0]

print(f"  Wall clock (ms):")
print(f"    Min    : {min_track:.2f}")
print(f"    Avg    : {avg_track:.2f}")
print(f"    p50    : {p50_track:.2f}")
print(f"    p95    : {p95_track:.2f}")
print(f"    FPS    : {1000.0/avg_track:.1f}")
print()

if yolo_speed_inf:
    avg_pre_t  = sum(yolo_speed_pre)  / len(yolo_speed_pre)
    avg_inf_t  = sum(yolo_speed_inf)  / len(yolo_speed_inf)
    avg_post_t = sum(yolo_speed_post) / len(yolo_speed_post)
    print(f"  Ultralytics speed dict (ms, averaged):")
    print(f"    preprocess  : {avg_pre_t:.2f}")
    print(f"    inference   : {avg_inf_t:.2f}")
    print(f"    postprocess : {avg_post_t:.2f}")
    print(f"    sum         : {avg_pre_t + avg_inf_t + avg_post_t:.2f}")
    est_tracker = avg_track - (avg_pre_t + avg_inf_t + avg_post_t)
    print(f"    tracker+overhead: {est_tracker:.2f}  ← ByteTrack + CPU postproc")
print()

# ================================================================
# SECTION 8: NVIDIA-SMI SNAPSHOT
# ================================================================

print("=" * 70)
print("SECTION 8 — GPU UTILIZATION SNAPSHOT (nvidia-smi)")
print("=" * 70)
try:
    smi = subprocess.run(
        ["nvidia-smi",
         "--query-gpu=name,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5
    )
    if smi.returncode == 0:
        for line in smi.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                print(f"  Name       : {parts[0]}")
                print(f"  GPU util   : {parts[1]}%")
                print(f"  MEM util   : {parts[2]}%")
                print(f"  VRAM used  : {parts[3]} MiB / {parts[4]} MiB")
                print(f"  Power draw : {parts[5]} W")
    else:
        print(f"  nvidia-smi failed: {smi.stderr.strip()}")
except FileNotFoundError:
    print("  nvidia-smi not found in PATH")
except Exception as e:
    print(f"  Error: {e}")
print()

# ================================================================
# SECTION 9: VRAM ALLOCATION
# ================================================================

if use_gpu:
    print("=" * 70)
    print("SECTION 9 — VRAM ALLOCATION AFTER BENCHMARK")
    print("=" * 70)
    alloc = torch.cuda.memory_allocated(0) / 1024**2
    reserved = torch.cuda.memory_reserved(0) / 1024**2
    peak = torch.cuda.max_memory_allocated(0) / 1024**2
    print(f"  Allocated  : {alloc:.1f} MiB")
    print(f"  Reserved   : {reserved:.1f} MiB")
    print(f"  Peak       : {peak:.1f} MiB")
    print()

# ================================================================
# SECTION 10: DIAGNOSIS
# ================================================================

print("=" * 70)
print("SECTION 10 — DIAGNOSIS SUMMARY")
print("=" * 70)

raw_yolo_fps   = 1000.0 / avg_wall
track_fps      = 1000.0 / avg_track

print(f"  Raw YOLO avg wall    : {avg_wall:.1f} ms  ({raw_yolo_fps:.1f} fps)")
print(f"  YOLO+ByteTrack avg   : {avg_track:.1f} ms  ({track_fps:.1f} fps)")
tracker_overhead = avg_track - avg_wall
print(f"  ByteTrack overhead   : {tracker_overhead:.1f} ms")
print()

if avg_wall > 100:
    print("  *** DIAGNOSIS: YOLO is slow even without tracker.")
    print("      Possible causes:")
    print("      - Model is running on CPU despite device=0 config")
    print("      - Missing FP16 / model not half-precision")
    print("      - CUDA not properly initialised in WSL2")
    print(f"      - Model device: {next(vehicle_model.model.parameters()).device}")
elif tracker_overhead > 50:
    print("  *** DIAGNOSIS: YOLO is fast but ByteTrack adds significant overhead.")
    print("      ByteTrack update is CPU-bound (expected for pure Python tracker).")
    print("      Next step: evaluate detector cadence to reduce tracker call freq.")
else:
    print("  *** DIAGNOSIS: Both YOLO and tracker are performing well on GPU.")
    print(f"      Processing FPS: {track_fps:.1f}")
print("=" * 70)
