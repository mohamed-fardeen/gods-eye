from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import cv2

from app.detection.plate_detector import (
    PlateDetector,
    crop_plate,
)
from app.ocr.video_ocr import FineTunedPaddleOCR
from app.tracking.vehicle_tracker import VehicleTracker


@dataclass
class ANPRObservation:
    frame_id: int
    timestamp: float

    vehicle_id: int
    vehicle_type: str
    vehicle_confidence: float

    plate_bbox: tuple[int, int, int, int]
    plate_detection_confidence: float

    plate_text: str
    ocr_confidence: float


@dataclass
class PendingOCR:
    crop_path: Path
    frame_id: int
    timestamp: float
    vehicle_id: int
    vehicle_type: str
    vehicle_confidence: float
    plate_bbox: tuple[int, int, int, int]
    plate_detection_confidence: float


class IntegratedANPR:
    """
    Integrated ANPR pipeline:

        video
          ↓
        vehicle detection
          ↓
        ByteTrack
          ↓
        plate detection
          ↓
        vehicle ↔ plate association
          ↓
        plate crop
          ↓
        fine-tuned PP-OCRv6
          ↓
        OCR result
          ↓
        annotate original frame
          ↓
        write video
    """

    def __init__(
        self,
        vehicle_model: str = "yolov8n.pt",
        plate_model: str = (
            "models/plate_detector/weights/best.pt"
        ),
        device: int | str = 0,
    ) -> None:

        self.vehicle_tracker = VehicleTracker(
            model_path=vehicle_model,
            device=device,
        )

        self.plate_detector = PlateDetector(
            model_path=plate_model,
            device=device,
        )

        self.ocr = FineTunedPaddleOCR()

    @staticmethod
    def plate_belongs_to_vehicle(
        vehicle_bbox: tuple[int, int, int, int],
        plate_bbox: tuple[int, int, int, int],
    ) -> bool:
        """
        A plate is associated with a vehicle when the plate
        center lies inside that vehicle's bounding box.
        """

        vx1, vy1, vx2, vy2 = vehicle_bbox
        px1, py1, px2, py2 = plate_bbox

        plate_cx = (px1 + px2) / 2.0
        plate_cy = (py1 + py2) / 2.0

        return (
            vx1 <= plate_cx <= vx2
            and vy1 <= plate_cy <= vy2
        )

    @staticmethod
    def _draw_vehicle_without_plate(
        frame,
        vehicle,
    ) -> None:

        x1, y1, x2, y2 = vehicle.bbox

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 255),
            2,
        )

        label = (
            f"ID {vehicle.track_id} | "
            "PLATE: --"
        )

        cv2.putText(
            frame,
            label,
            (x1, max(25, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2,
        )

    @staticmethod
    def _draw_pending_plate(
        frame,
        vehicle,
        plate,
    ) -> None:

        vx1, vy1, vx2, vy2 = vehicle.bbox

        px1, py1, px2, py2 = plate.bbox

        cv2.rectangle(
            frame,
            (vx1, vy1),
            (vx2, vy2),
            (0, 255, 0),
            2,
        )

        cv2.rectangle(
            frame,
            (px1, py1),
            (px2, py2),
            (255, 0, 0),
            2,
        )

        label = (
            f"ID {vehicle.track_id} | "
            "OCR: processing..."
        )

        cv2.putText(
            frame,
            label,
            (vx1, max(25, vy1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
        )

    @staticmethod
    def _draw_ocr_result(
        frame,
        metadata: PendingOCR,
        text: str,
        ocr_confidence: float,
    ) -> None:

        vx1 = None

        # Vehicle box is not stored in PendingOCR, so we draw
        # the plate annotation first. The plate bbox is enough
        # to produce a readable annotation.
        px1, py1, px2, py2 = metadata.plate_bbox

        cv2.rectangle(
            frame,
            (px1, py1),
            (px2, py2),
            (255, 0, 0),
            2,
        )

        if text:
            plate_label = (
                f"{text} "
                f"({ocr_confidence:.2f})"
            )
        else:
            plate_label = (
                f"UNREADABLE "
                f"({ocr_confidence:.2f})"
            )

        text_y = max(25, py1 - 8)

        cv2.putText(
            frame,
            plate_label,
            (px1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (255, 0, 0),
            2,
        )

    def _process_ocr_batch(
        self,
        pending_items: list[PendingOCR],
        frame_store: dict[int, object],
        observations: list[ANPRObservation],
    ) -> None:

        if not pending_items:
            return

        crop_paths = [
            item.crop_path
            for item in pending_items
        ]

        predictions = self.ocr.read_batch(
            crop_paths
        )

        for item in pending_items:

            frame = frame_store.get(
                item.frame_id
            )

            if frame is None:
                continue

            result = predictions.get(
                item.crop_path.name
            )

            if result is None:
                text = ""
                confidence = 0.0
            else:
                text, confidence = result

            text = text.strip()

            # Draw OCR onto the ORIGINAL frame.
            self._draw_ocr_result(
                frame,
                item,
                text,
                confidence,
            )

            observations.append(
                ANPRObservation(
                    frame_id=item.frame_id,
                    timestamp=item.timestamp,
                    vehicle_id=item.vehicle_id,
                    vehicle_type=item.vehicle_type,
                    vehicle_confidence=item.vehicle_confidence,
                    plate_bbox=item.plate_bbox,
                    plate_detection_confidence=(
                        item.plate_detection_confidence
                    ),
                    plate_text=text,
                    ocr_confidence=confidence,
                )
            )

    @staticmethod
    def expand_vehicle_bbox(
        bbox: tuple[int, int, int, int],
        frame_width: int,
        frame_height: int,
    ) -> tuple[int, int, int, int]:
        # Simple passthrough since it wasn't defined in the snippet
        x1, y1, x2, y2 = bbox
        return max(0, x1), max(0, y1), min(frame_width, x2), min(frame_height, y2)

    def run(
        self,
        video_path: str,
        output_video: str = (
            "outputs/integrated_anpr.mp4"
        ),
        crop_dir: str = (
            "outputs/integrated_plate_crops"
        ),
        max_frames: int = 0,
        ocr_batch_size: int = 16,
    ) -> list[ANPRObservation]:

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        output_video = Path(output_video)
        output_video.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        crop_dir = Path(crop_dir)
        crop_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        observations: list[ANPRObservation] = []

        # OCR jobs waiting to be processed.
        pending_ocr: list[PendingOCR] = []

        # Frames waiting to be written.
        #
        # IMPORTANT:
        # We keep ALL frames here, not only frames
        # containing OCR detections.
        frame_store: dict[int, object] = {}

        writer = None

        # The next frame that MUST be written.
        #
        # This guarantees chronological video output.
        next_frame_to_write = 0

        def write_frame(
            fid: int,
            image,
        ) -> None:

            nonlocal writer

            if writer is None:

                height, width = image.shape[:2]

                writer = cv2.VideoWriter(
                    str(output_video),
                    cv2.VideoWriter_fourcc(
                        *"mp4v"
                    ),
                    25.0,
                    (width, height),
                )

                if not writer.isOpened():
                    raise RuntimeError(
                        f"Could not open video writer: "
                        f"{output_video}"
                    )

            writer.write(image)

        for (
            frame_id,
            frame,
            vehicles,
        ) in self.vehicle_tracker.process_video(
            str(video_path)
        ):

            if (
                max_frames > 0
                and frame_id >= max_frames
            ):
                break

            # -------------------------------------------------
            # STORE EVERY FRAME
            # -------------------------------------------------
            frame_store[frame_id] = frame.copy()

            timestamp = frame_id / 25.0

            frame_height, frame_width = (
                frame.shape[:2]
            )

            # -------------------------------------------------
            # PROCESS EACH TRACKED VEHICLE
            # -------------------------------------------------
            for vehicle in vehicles:

                # We detect plates INSIDE each vehicle ROI.
                vx1, vy1, vx2, vy2 = (
                    self.expand_vehicle_bbox(
                        vehicle.bbox,
                        frame_width,
                        frame_height,
                    )
                )

                vehicle_roi = frame[
                    vy1:vy2,
                    vx1:vx2,
                ]

                if (
                    vehicle_roi is None
                    or vehicle_roi.size == 0
                ):
                    self._draw_vehicle_without_plate(
                        frame_store[frame_id],
                        vehicle,
                    )
                    continue

                # -------------------------------------------------
                # PLATE DETECTION FOR THIS VEHICLE
                # -------------------------------------------------
                roi_plates = self.plate_detector.detect(
                    vehicle_roi,
                )

                if not roi_plates:

                    # This means:
                    # vehicle detected,
                    # but plate detector did not find a plate
                    # on THIS frame.
                    #
                    # We do NOT use old OCR here.
                    self._draw_vehicle_without_plate(
                        frame_store[frame_id],
                        vehicle,
                    )

                    continue

                # Adjust the detected plate bbox to global coordinates
                for p in roi_plates:
                    px1, py1, px2, py2 = p.bbox
                    p.bbox = (px1 + vx1, py1 + vy1, px2 + vx1, py2 + vy1)

                # Strongest plate detection.
                plate = max(
                    roi_plates,
                    key=lambda p: p.confidence,
                )

                plate_crop = crop_plate(
                    frame,
                    plate.bbox,
                )

                if plate_crop is None:

                    self._draw_vehicle_without_plate(
                        frame_store[frame_id],
                        vehicle,
                    )

                    continue

                # -------------------------------------------------
                # SAVE PLATE CROP
                # -------------------------------------------------
                crop_filename = (
                    f"frame_{frame_id:06d}"
                    f"_vehicle_{vehicle.track_id}"
                    f"_plate_0.jpg"
                )

                crop_path = (
                    crop_dir / crop_filename
                )

                ok = cv2.imwrite(
                    str(crop_path),
                    plate_crop,
                )

                if not ok:
                    continue

                # -------------------------------------------------
                # QUEUE OCR
                # -------------------------------------------------
                pending_ocr.append(
                    PendingOCR(
                        crop_path=crop_path,
                        frame_id=frame_id,
                        timestamp=timestamp,
                        vehicle_id=vehicle.track_id,
                        vehicle_type=vehicle.class_name,
                        vehicle_confidence=(
                            vehicle.confidence
                        ),
                        plate_bbox=plate.bbox,
                        plate_detection_confidence=(
                            plate.confidence
                        ),
                    )
                )

                # Draw plate and vehicle immediately.
                self._draw_pending_plate(
                    frame_store[frame_id],
                    vehicle,
                    plate,
                )

            # -------------------------------------------------
            # OCR BATCH
            # -------------------------------------------------
            if len(pending_ocr) >= ocr_batch_size:

                # Remember the newest frame involved in this
                # OCR batch.
                max_ocr_frame = max(
                    item.frame_id
                    for item in pending_ocr
                )

                # Run OCR.
                self._process_ocr_batch(
                    pending_ocr,
                    frame_store,
                    observations,
                )

                # -------------------------------------------------
                # CRITICAL FIX:
                #
                # Write EVERY frame sequentially up to the
                # newest OCR frame.
                #
                # Previously we wrote only OCR frames, which
                # destroyed the video's chronological order.
                # -------------------------------------------------
                while (
                    next_frame_to_write
                    <= max_ocr_frame
                ):

                    completed_frame = (
                        frame_store.pop(
                            next_frame_to_write,
                            None,
                        )
                    )

                    if completed_frame is not None:

                        write_frame(
                            next_frame_to_write,
                            completed_frame,
                        )

                    next_frame_to_write += 1

                pending_ocr.clear()

        # -----------------------------------------------------
        # PROCESS REMAINING OCR
        # -----------------------------------------------------
        if pending_ocr:

            max_ocr_frame = max(
                item.frame_id
                for item in pending_ocr
            )

            self._process_ocr_batch(
                pending_ocr,
                frame_store,
                observations,
            )

            while (
                next_frame_to_write
                <= max_ocr_frame
            ):

                completed_frame = (
                    frame_store.pop(
                        next_frame_to_write,
                        None,
                    )
                )

                if completed_frame is not None:

                    write_frame(
                        next_frame_to_write,
                        completed_frame,
                    )

                next_frame_to_write += 1

        # -----------------------------------------------------
        # WRITE ANY REMAINING FRAMES
        # -----------------------------------------------------
        remaining_ids = sorted(
            frame_store.keys()
        )

        for fid in remaining_ids:

            # Preserve chronological ordering.
            if fid < next_frame_to_write:
                continue

            write_frame(
                fid,
                frame_store[fid],
            )

            next_frame_to_write = fid + 1

        if writer is not None:
            writer.release()

        return observations
