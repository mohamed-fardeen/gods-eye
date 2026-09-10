from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import cv2

from anpr.tracking.vehicle_tracker import VehicleTracker


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video",
        required=True,
        help="Input video path",
    )

    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="YOLO vehicle model",
    )

    parser.add_argument(
        "--device",
        default="0",
        help="CUDA device, e.g. 0 or cpu",
    )

    parser.add_argument(
        "--output",
        default="outputs/tracking_preview.mp4",
        help="Output annotated video",
    )

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    device = (
        int(args.device)
        if str(args.device).isdigit()
        else args.device
    )

    tracker = VehicleTracker(
        model_path=args.model,
        device=device,
    )

    writer = None

    unique_tracks: set[int] = set()
    frame_count = 0

    for frame_id, frame, observations in tracker.process_video(
        args.video
    ):
        frame_count += 1

        for obs in observations:
            if obs.track_id >= 0:
                unique_tracks.add(obs.track_id)

            x1, y1, x2, y2 = obs.bbox

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            label = (
                f"ID {obs.track_id} "
                f"{obs.class_name} "
                f"{obs.confidence:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
            )

        if writer is None:
            height, width = frame.shape[:2]

            fps = 25.0

            writer = cv2.VideoWriter(
                str(output_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height),
            )

        writer.write(frame)

        if frame_id % 100 == 0:
            print(
                f"Processed frame={frame_id} "
                f"active_tracks={len(unique_tracks)}"
            )

    if writer is not None:
        writer.release()

    print()
    print("=" * 60)
    print("VEHICLE TRACKING TEST")
    print("=" * 60)
    print(f"Frames processed : {frame_count}")
    print(f"Unique tracks    : {len(unique_tracks)}")
    print(f"Output video     : {output_path.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
