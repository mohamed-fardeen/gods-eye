"""
License plate detector.

Wraps the YOLOv8 model fine-tuned on Indian plate data (models/plate_detector_best.pt,
produced by scripts/train_plate_detector.py — MILESTONE 6). Falls back to the
pretrained COCO model + a heuristic (won't find plates well) ONLY so the rest
of the pipeline stays runnable before training finishes; a clear warning is
printed so you never mistake fallback output for real detection.
"""

import os
import warnings
from dataclasses import dataclass
from ultralytics import YOLO

DEFAULT_CHECKPOINT = "models/plate_detector_best.pt"


@dataclass
class PlateDetection:
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float


class PlateDetector:
    def __init__(self, checkpoint: str = DEFAULT_CHECKPOINT, device: str = "cuda:0", conf_threshold: float = 0.35):
        if not os.path.exists(checkpoint):
            warnings.warn(
                f"[PlateDetector] Fine-tuned checkpoint not found at '{checkpoint}'. "
                "Falling back to a generic pretrained model — plate localization will be "
                "unreliable until MILESTONE 6 training completes and you point this at "
                "the real checkpoint. Do not trust results until this warning is gone.",
                stacklevel=2,
            )
            checkpoint = "yolov8n.pt"
        self.model = YOLO(checkpoint)
        self.device = device
        self.conf_threshold = conf_threshold

    def detect(self, vehicle_crop_bgr) -> list[PlateDetection]:
        """Run on a vehicle crop (not the full frame) — restricting search
        area to the vehicle's bbox cuts false positives and is much faster."""
        results = self.model.predict(
            vehicle_crop_bgr, device=self.device, conf=self.conf_threshold, verbose=False
        )
        out: list[PlateDetection] = []
        if not results or results[0].boxes is None:
            return out
        for box, conf in zip(results[0].boxes.xyxy.cpu().numpy(), results[0].boxes.conf.cpu().numpy()):
            out.append(PlateDetection(bbox_xyxy=tuple(float(v) for v in box), confidence=float(conf)))
        return out
