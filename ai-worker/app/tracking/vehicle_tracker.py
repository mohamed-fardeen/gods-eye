from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
from ultralytics import YOLO


@dataclass
class VehicleObservation:
    frame_id: int
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]


class VehicleTracker:
    """
    YOLO vehicle detector + ByteTrack.

    COCO classes used:
        2  = car
        3  = motorcycle
        5  = bus
        7  = truck
    """

    VEHICLE_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.5,
        device: int | str = 0,
    ) -> None:
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device

    def process_video(
        self,
        video_path: str,
    ) -> Iterator[tuple[int, object, list[VehicleObservation]]]:
        """
        Yields:
            frame_id
            frame
            vehicle observations
        """

        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"Video not found: {video}")

        results = self.model.track(
            source=str(video),
            stream=True,
            persist=True,
            tracker="bytetrack.yaml",
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=list(self.VEHICLE_CLASSES.keys()),
            device=self.device,
            verbose=False,
        )

        for frame_id, result in enumerate(results):
            frame = result.orig_img
            observations: list[VehicleObservation] = []

            if result.boxes is None:
                yield frame_id, frame, observations
                continue

            boxes = result.boxes

            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            classes = boxes.cls.cpu().numpy().astype(int)

            if boxes.id is not None:
                track_ids = (
                    boxes.id.cpu()
                    .numpy()
                    .astype(int)
                )
            else:
                track_ids = [-1] * len(xyxy)

            for bbox, confidence, class_id, track_id in zip(
                xyxy,
                confs,
                classes,
                track_ids,
            ):
                if class_id not in self.VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, bbox)

                observations.append(
                    VehicleObservation(
                        frame_id=frame_id,
                        track_id=int(track_id),
                        class_id=int(class_id),
                        class_name=self.VEHICLE_CLASSES[class_id],
                        confidence=float(confidence),
                        bbox=(x1, y1, x2, y2),
                    )
                )

            yield frame_id, frame, observations
