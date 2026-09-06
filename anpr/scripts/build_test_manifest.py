from __future__ import annotations

import csv
from pathlib import Path


GT_FILE = Path("data/processed/sai_split/test.csv")
CROP_DIR = Path("outputs/test_plate_crops")
OUTPUT = Path("outputs/test_manifest.csv")


def main() -> None:
    with GT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        gt_rows = list(csv.DictReader(f))

    crop_files = sorted(
        p
        for p in CROP_DIR.iterdir()
        if p.is_file()
    )

    rows = []

    for gt in gt_rows:
        source_filename = gt.get("yolo_image_name") or Path(gt["image_path"]).name
        source_stem = Path(source_filename).stem

        matching_crops = [
            crop
            for crop in crop_files
            if crop.name.startswith(source_stem + "_plate_")
        ]

        if not matching_crops:
            rows.append(
                {
                    "source_image": source_filename,
                    "ground_truth": gt["plate_text"],
                    "crop": "",
                    "crop_count": 0,
                }
            )

            continue

        for crop in matching_crops:
            rows.append(
                {
                    "source_image": source_filename,
                    "ground_truth": gt["plate_text"],
                    "crop": str(crop),
                    "crop_count": len(matching_crops),
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_image",
                "ground_truth",
                "crop",
                "crop_count",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Manifest rows: {len(rows)}")
    print(f"Saved to: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
