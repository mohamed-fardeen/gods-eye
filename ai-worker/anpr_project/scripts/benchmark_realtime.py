#!/usr/bin/env python3
"""
Benchmark the realtime ANPR pipeline.

Expected realtime pipeline:
    app/realtime/realtime_anpr.py

This script:
1. Runs the realtime ANPR pipeline on a supplied video.
2. Captures stdout/stderr.
3. Extracts performance metrics when they are printed by the pipeline.
4. Prints a standardized REAL-TIME ANPR PERFORMANCE report.

Usage:
    python scripts/benchmark_realtime.py --video path/to/test_clip.mp4
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REALTIME_SCRIPT = PROJECT_ROOT / "app" / "realtime" / "realtime_anpr.py"


def extract_float(text: str, patterns: list[str]) -> float | None:
    """Return the first float matching one of the supplied regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (TypeError, ValueError):
                pass
    return None


def extract_int(text: str, patterns: list[str]) -> int | None:
    """Return the first integer matching one of the supplied regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (TypeError, ValueError):
                pass
    return None


def parse_metrics(output: str) -> dict[str, float | int | None]:
    """
    Parse metrics printed by realtime_anpr.py.

    Supports labels such as:
        Input FPS
        Processing FPS
        Average latency
        Vehicle detections
        Plate observations
        OCR observations
        GPU VRAM
    """

    return {
        "input_fps": extract_float(
            output,
            [
                r"Input\s*FPS\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)",
                r"Input\s*frame\s*rate\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)",
            ],
        ),
        "processing_fps": extract_float(
            output,
            [
                r"Processing\s*FPS\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)",
                r"Process(?:ing)?\s*frame\s*rate\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)",
            ],
        ),
        "latency_ms": extract_float(
            output,
            [
                r"Average\s*latency\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*ms",
                r"Latency\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*ms",
            ],
        ),
        "vehicle_detections": extract_int(
            output,
            [
                r"Vehicle\s*detections\s*[:=]\s*(\d+)",
                r"Vehicles?\s*detected\s*[:=]\s*(\d+)",
            ],
        ),
        "plate_observations": extract_int(
            output,
            [
                r"Plate\s*observations\s*[:=]\s*(\d+)",
                r"Plates?\s*observed\s*[:=]\s*(\d+)",
            ],
        ),
        "ocr_observations": extract_int(
            output,
            [
                r"OCR\s*observations\s*[:=]\s*(\d+)",
                r"OCR\s*reads?\s*[:=]\s*(\d+)",
            ],
        ),
        "gpu_vram_gb": extract_float(
            output,
            [
                r"GPU\s*VRAM\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*GB",
                r"VRAM\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*GB",
            ],
        ),
    }


def get_video_info(video_path: Path) -> tuple[float | None, int | None]:
    """
    Read input FPS and frame count using OpenCV.
    """
    try:
        import cv2
    except ImportError:
        return None, None

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return None, None

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    cap.release()

    input_fps = fps if fps and fps > 0 else None
    frames = int(frame_count) if frame_count and frame_count > 0 else None

    return input_fps, frames


def run_realtime_pipeline(video_path: Path) -> tuple[int, str, float]:
    """
    Execute realtime_anpr.py and capture complete console output.

    Returns:
        return_code
        combined_output
        wall_clock_seconds
    """

    command = [
        sys.executable,
        str(REALTIME_SCRIPT),
        "--source",
        str(video_path),
    ]

    print("\nRunning realtime ANPR pipeline:")
    print(" ".join(f'"{x}"' if " " in x else x for x in command))
    print()

    start = time.perf_counter()

    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    elapsed = time.perf_counter() - start

    output = ""

    if process.stdout:
        output += process.stdout

    if process.stderr:
        output += "\n" + process.stderr

    return process.returncode, output, elapsed


def print_report(
    metrics: dict[str, float | int | None],
    elapsed_seconds: float,
    detected_input_fps: float | None,
    frame_count: int | None,
    return_code: int,
) -> None:
    """
    Print standardized benchmark report.
    """

    input_fps = metrics["input_fps"] or detected_input_fps

    processing_fps = metrics["processing_fps"]

    # Fallback wall-clock processing FPS if realtime_anpr.py
    # did not print its own Processing FPS.
    if processing_fps is None and frame_count and elapsed_seconds > 0:
        processing_fps = frame_count / elapsed_seconds

    print()
    print("=" * 50)
    print("REAL-TIME ANPR PERFORMANCE")
    print("=" * 50)

    if input_fps is not None:
        print(f"Input FPS          : {input_fps:.1f}")
    else:
        print("Input FPS          : N/A")

    if processing_fps is not None:
        print(f"Processing FPS     : {processing_fps:.1f}")
    else:
        print("Processing FPS     : N/A")

    if metrics["latency_ms"] is not None:
        print(f"Average latency    : {metrics['latency_ms']:.1f} ms")
    else:
        print("Average latency    : N/A")

    if metrics["vehicle_detections"] is not None:
        print(f"Vehicle detections : {metrics['vehicle_detections']}")
    else:
        print("Vehicle detections : N/A")

    if metrics["plate_observations"] is not None:
        print(f"Plate observations : {metrics['plate_observations']}")
    else:
        print("Plate observations : N/A")

    if metrics["ocr_observations"] is not None:
        print(f"OCR observations   : {metrics['ocr_observations']}")
    else:
        print("OCR observations   : N/A")

    if metrics["gpu_vram_gb"] is not None:
        print(f"GPU VRAM           : {metrics['gpu_vram_gb']:.2f} GB")
    else:
        print("GPU VRAM           : N/A")

    print(f"Wall-clock time    : {elapsed_seconds:.2f} s")
    print(f"Pipeline exit code : {return_code}")

    print("=" * 50)

    # Performance decision
    if input_fps is not None and processing_fps is not None:
        ratio = processing_fps / input_fps

        print()
        print("PERFORMANCE ASSESSMENT")
        print("-" * 50)

        if ratio >= 1.0:
            print("PASS: Processing FPS >= Input FPS")
            print("The pipeline can keep up with the video stream.")
        elif ratio >= 0.85:
            print("BORDERLINE: Processing FPS is slightly below Input FPS")
            print("The pipeline is close to realtime but still has processing headroom to recover.")
        else:
            print("FAIL: Processing FPS is materially below Input FPS")
            print("The pipeline will accumulate latency on a continuous stream.")

        print(f"Realtime ratio    : {ratio:.2f}x")

    if return_code != 0:
        print()
        print("WARNING: realtime_anpr.py exited with a non-zero status.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark the realtime ANPR pipeline."
    )

    parser.add_argument(
        "--video",
        required=True,
        help="Path to the video used for the realtime benchmark.",
    )

    args = parser.parse_args()

    video_path = Path(args.video).expanduser().resolve()

    if not video_path.exists():
        print(f"ERROR: Video does not exist: {video_path}")
        return 1

    if not REALTIME_SCRIPT.exists():
        print(
            "ERROR: Realtime pipeline script was not found:\n"
            f"  {REALTIME_SCRIPT}"
        )
        return 1

    print("=" * 50)
    print("ANPR REALTIME BENCHMARK")
    print("=" * 50)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Video        : {video_path}")
    print(f"Pipeline     : {REALTIME_SCRIPT}")

    detected_input_fps, frame_count = get_video_info(video_path)

    if detected_input_fps is not None:
        print(f"Video FPS    : {detected_input_fps:.2f}")

    if frame_count is not None:
        print(f"Frame count  : {frame_count}")

    return_code, output, elapsed_seconds = run_realtime_pipeline(video_path)

    metrics = parse_metrics(output)

    # Print the raw realtime pipeline output when parsing failed,
    # so debugging is straightforward.
    missing_core_metrics = (
        metrics["processing_fps"] is None
        and metrics["latency_ms"] is None
        and metrics["vehicle_detections"] is None
    )

    if missing_core_metrics:
        print()
        print("=" * 50)
        print("RAW REALTIME PIPELINE OUTPUT")
        print("=" * 50)
        print(output)
        print("=" * 50)

    print_report(
        metrics=metrics,
        elapsed_seconds=elapsed_seconds,
        detected_input_fps=detected_input_fps,
        frame_count=frame_count,
        return_code=return_code,
    )

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
