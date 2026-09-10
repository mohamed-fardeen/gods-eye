from __future__ import annotations

import argparse
import csv
from pathlib import Path

from anpr.pipeline.integrated_anpr import IntegratedANPR


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video",
        required=True,
    )

    parser.add_argument(
        "--device",
        default="0",
    )

    parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--output",
        default="outputs/integrated_anpr.mp4",
    )

    parser.add_argument(
        "--csv",
        default="outputs/integrated_observations.csv",
    )

    args = parser.parse_args()

    device = (
        int(args.device)
        if str(args.device).isdigit()
        else args.device
    )

    pipeline = IntegratedANPR(
        vehicle_model="yolov8n.pt",
        plate_model=(
            "models/plate_detector/weights/best.pt"
        ),
        device=device,
    )

    observations = pipeline.run(
        video_path=args.video,
        output_video=args.output,
        max_frames=args.max_frames,
        ocr_batch_size=16,
    )

    output_csv = Path(args.csv)

    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "frame_id",
                "timestamp",
                "vehicle_id",
                "vehicle_type",
                "vehicle_confidence",
                "plate_x1",
                "plate_y1",
                "plate_x2",
                "plate_y2",
                "plate_detection_confidence",
                "plate_text",
                "ocr_confidence",
            ]
        )

        for obs in observations:

            x1, y1, x2, y2 = obs.plate_bbox

            writer.writerow(
                [
                    obs.frame_id,
                    f"{obs.timestamp:.3f}",
                    obs.vehicle_id,
                    obs.vehicle_type,
                    f"{obs.vehicle_confidence:.6f}",
                    x1,
                    y1,
                    x2,
                    y2,
                    f"{obs.plate_detection_confidence:.6f}",
                    obs.plate_text,
                    f"{obs.ocr_confidence:.6f}",
                ]
            )

    unique_vehicles = sorted(
        {
            obs.vehicle_id
            for obs in observations
            if obs.vehicle_id >= 0
        }
    )

    print()
    print("=" * 70)
    print("INTEGRATED ANPR")
    print("=" * 70)
    print(
        f"Observations                  : "
        f"{len(observations)}"
    )
    print(
        f"Vehicles with OCR observations: "
        f"{len(unique_vehicles)}"
    )
    print(
        f"Video output                  : "
        f"{Path(args.output).resolve()}"
    )
    print(
        f"CSV output                    : "
        f"{output_csv.resolve()}"
    )
    print("=" * 70)

    print("\nSample observations:")

    for obs in observations[:20]:

        print(
            f"frame={obs.frame_id:<6} "
            f"vehicle={obs.vehicle_id:<4} "
            f"plate={obs.plate_text:<15} "
            f"plate_conf="
            f"{obs.plate_detection_confidence:.2f} "
            f"ocr_conf="
            f"{obs.ocr_confidence:.2f}"
        )


if __name__ == "__main__":
    main()
