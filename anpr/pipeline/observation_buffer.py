from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlateObservation:
    vehicle_id: int
    frame_id: int
    timestamp: float

    plate_bbox: tuple[int, int, int, int]

    crop_path: Optional[str] = None

    plate_detection_confidence: float = 0.0

    quality_score: float = 0.0

    ocr_text: str = ""
    ocr_confidence: float = 0.0


class ObservationBuffer:
    """
    Maintains recent plate observations for each tracked vehicle.

    This is the foundation for temporal evidence fusion.
    """

    def __init__(
        self,
        max_observations_per_vehicle: int = 30,
    ) -> None:

        self.max_observations = max_observations_per_vehicle

        self.buffers: dict[
            int,
            deque[PlateObservation]
        ] = defaultdict(
            lambda: deque(
                maxlen=self.max_observations
            )
        )

    def add(
        self,
        observation: PlateObservation,
    ) -> None:
        self.buffers[
            observation.vehicle_id
        ].append(observation)

    def get(
        self,
        vehicle_id: int,
    ) -> list[PlateObservation]:

        return list(
            self.buffers.get(
                vehicle_id,
                []
            )
        )

    def get_best_quality(
        self,
        vehicle_id: int,
    ) -> Optional[PlateObservation]:

        observations = self.get(vehicle_id)

        if not observations:
            return None

        return max(
            observations,
            key=lambda x: x.quality_score,
        )

    def clear_vehicle(
        self,
        vehicle_id: int,
    ) -> None:

        self.buffers.pop(
            vehicle_id,
            None,
        )

    def active_vehicle_ids(
        self,
    ) -> list[int]:

        return list(self.buffers.keys())

    def summary(self) -> dict:

        return {
            vehicle_id: len(observations)
            for vehicle_id, observations
            in self.buffers.items()
        }
