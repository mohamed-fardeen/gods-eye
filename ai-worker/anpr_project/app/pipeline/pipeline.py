"""
End-to-end Temporal Quality-Aware ANPR pipeline.

CCTV video -> vehicle detect+track -> plate detect -> quality score
-> select informative observations -> perspective correct -> enhance
-> OCR -> temporal fusion -> Indian validation -> final plate / status

Run: python -m app.pipeline.pipeline --video path/to/video.mp4
"""

import argparse
import csv
from collections import defaultdict
from dataclasses import asdict

import cv2

from app.tracking.tracker import VehicleTracker
from app.plate.plate_detector import PlateDetector
from app.quality.quality_scorer import score_plate_crop
from app.preprocessing.enhance import correct_perspective, enhance_for_ocr
from app.ocr.ocr_engine import OCREngine
from app.fusion.temporal_fusion import Observation, fuse_observations

# Only OCR observations above this quality get spent on OCR compute at all —
# implements MILESTONE 15 "selective OCR", not every frame.
MIN_QUALITY_TO_OCR = 0.35
# Cap stored observations per vehicle to bound memory on long tracks.
MAX_OBSERVATIONS_PER_VEHICLE = 20


def run_pipeline(video_path: str, output_csv: str = "outputs/track_results.csv", device: str = "cuda:0", max_frames: int | None = None):
    vehicle_tracker = VehicleTracker(device=device)
    plate_detector = PlateDetector(device=device)
    ocr_engine = OCREngine(engine="paddle", use_gpu=(device != "cpu"))

    # track_id -> list[Observation]
    buffers: dict[int, list[Observation]] = defaultdict(list)
    finalized: dict[int, dict] = {}

    cap = cv2.VideoCapture(video_path)
    frame_id = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if max_frames is not None and frame_id >= max_frames:
            break

        vehicles = vehicle_tracker.track_frame(frame)
        for v in vehicles:
            x1, y1, x2, y2 = [int(c) for c in v.bbox_xyxy]
            x1, y1 = max(x1, 0), max(y1, 0)
            vehicle_crop = frame[y1:y2, x1:x2]
            if vehicle_crop.size == 0:
                continue

            plates = plate_detector.detect(vehicle_crop)
            for p in plates:
                px1, py1, px2, py2 = [int(c) for c in p.bbox_xyxy]
                plate_crop = vehicle_crop[max(py1, 0):py2, max(px1, 0):px2]
                if plate_crop.size == 0:
                    continue

                quality = score_plate_crop(plate_crop)
                if quality.overall < MIN_QUALITY_TO_OCR:
                    continue  # selective OCR: skip clearly unusable crops

                corrected = correct_perspective(plate_crop)
                enhanced = enhance_for_ocr(corrected)

                candidates = ocr_engine.read(enhanced)
                if not candidates:
                    continue
                best = max(candidates, key=lambda c: c.confidence)

                obs = Observation(
                    frame_id=frame_id,
                    text=best.text,
                    ocr_confidence=best.confidence,
                    quality_score=quality.overall,
                    detection_confidence=p.confidence,
                )
                buffers[v.track_id].append(obs)
                if len(buffers[v.track_id]) > MAX_OBSERVATIONS_PER_VEHICLE:
                    # keep the highest-weight observations, drop the weakest
                    buffers[v.track_id].sort(key=lambda o: o.weight, reverse=True)
                    buffers[v.track_id] = buffers[v.track_id][:MAX_OBSERVATIONS_PER_VEHICLE]

        frame_id += 1

    cap.release()

    # Fuse every track once the video ends. (For live streams, re-run fusion
    # periodically per track and update the displayed result — the fusion
    # function is cheap and idempotent.)
    for track_id, observations in buffers.items():
        finalized[track_id] = asdict(fuse_observations(observations))

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["track_id", "final_plate", "confidence", "status", "num_observations", "evidence_frame_ids"])
        for track_id, result in finalized.items():
            writer.writerow([
                track_id, result["final_plate"], result["confidence"],
                result["status"], result["num_observations"], result["evidence_frame_ids"],
            ])

    print(f"Processed {frame_id} frames, {len(finalized)} tracked vehicles.")
    print(f"Results written to {output_csv}")
    return finalized


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--output", default="outputs/track_results.csv")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--max_frames", type=int, default=None)
    args = parser.parse_args()
    run_pipeline(args.video, args.output, args.device, args.max_frames)
