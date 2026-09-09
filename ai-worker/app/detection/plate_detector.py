from __future__ import annotations

from dataclasses import dataclass

import cv2
from ultralytics import YOLO


@dataclass
class PlateDetection:
    bbox: tuple[int, int, int, int]
    confidence: float


class PlateDetector:
    """
    Indian license-plate detector.

    Expects a YOLO model trained with one class:
        0 = plate
    """

    def __init__(
        self,
        model_path: str = "models/plate_detector/weights/best.pt",
        conf_threshold: float = 0.25,
        device: int | str = 0,
    ) -> None:
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.device = device

    def detect(
        self,
        frame,
    ) -> list[PlateDetection]:

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False,
        )

        if not results:
            return []

        result = results[0]

        if result.boxes is None:
            return []

        detections: list[PlateDetection] = []

        xyxy = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for bbox, confidence in zip(xyxy, confs):

            x1, y1, x2, y2 = map(int, bbox)

            detections.append(
                PlateDetection(
                    bbox=(x1, y1, x2, y2),
                    confidence=float(confidence),
                )
            )

        return detections


def crop_plate(
    frame,
    bbox: tuple[int, int, int, int],
):
    """
    Safely crop a detected plate from a frame.
    """

    height, width = frame.shape[:2]

    x1, y1, x2, y2 = bbox

    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2]
