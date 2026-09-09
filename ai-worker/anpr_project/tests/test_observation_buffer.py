from app.pipeline.observation_buffer import (
    ObservationBuffer,
    PlateObservation,
)


def main() -> None:

    buffer = ObservationBuffer(
        max_observations_per_vehicle=5
    )

    for frame_id in range(10):

        buffer.add(
            PlateObservation(
                vehicle_id=7,
                frame_id=frame_id,
                timestamp=frame_id / 25.0,
                plate_bbox=(10, 10, 100, 50),
                plate_detection_confidence=0.9,
                quality_score=frame_id / 10.0,
            )
        )

    observations = buffer.get(7)

    assert len(observations) == 5

    assert observations[0].frame_id == 5
    assert observations[-1].frame_id == 9

    best = buffer.get_best_quality(7)

    assert best is not None
    assert best.frame_id == 9

    print("Observation buffer test PASSED")
    print("Stored observations:", len(observations))
    print("Best frame:", best.frame_id)


if __name__ == "__main__":
    main()
