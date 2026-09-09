"""
Vehicle detection + tracking.

Uses Ultralytics YOLO's built-in `.track()` (ByteTrack under the hood) on a
COCO-pretrained model filtered to vehicle classes. We deliberately do NOT
fine-tune the vehicle detector — COCO vehicle classes (car, motorcycle, bus,
truck) are already high-accuracy and fine-tuning them would burn GPU budget
that's much better spent on the plate detector (see TRAINING STRATEGY).
"""

from dataclasses import dataclass
from ultralytics import YOLO

# COCO class ids for vehicles.
VEHICLE_CLASS_IDS = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


@dataclass
class TrackedVehicle:
    track_id: int
    cls_name: str
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float


class VehicleTracker:
    def __init__(self, model_name: str = "yolov8n.pt", device: str = "cuda:0"):
        self.model = YOLO(model_name)
        self.device = device

    def track_frame(self, frame) -> list[TrackedVehicle]:
        """Run tracking on a single frame; call sequentially per-video-frame
        so the tracker maintains temporal state (do not call in parallel)."""
        results = self.model.track(
            frame,
            persist=True,
            classes=list(VEHICLE_CLASS_IDS.keys()),
            device=self.device,
            verbose=False,
        )
        out: list[TrackedVehicle] = []
        if not results or results[0].boxes is None or results[0].boxes.id is None:
            return out

        boxes = results[0].boxes
        for box, track_id, cls_id, conf in zip(
            boxes.xyxy.cpu().numpy(),
            boxes.id.cpu().numpy(),
            boxes.cls.cpu().numpy(),
            boxes.conf.cpu().numpy(),
        ):
            out.append(
                TrackedVehicle(
                    track_id=int(track_id),
                    cls_name=VEHICLE_CLASS_IDS.get(int(cls_id), "vehicle"),
                    bbox_xyxy=tuple(float(v) for v in box),
                    confidence=float(conf),
                )
            )
        return out
