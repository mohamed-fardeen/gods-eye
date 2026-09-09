from __future__ import annotations

import csv
from pathlib import Path

import cv2


TEST_CSV = Path("data/processed/sai_split/test.csv")
OUTPUT_DIR = Path("outputs/gt_plate_crops")


def main() -> None:
    if not TEST_CSV.exists():
        raise FileNotFoundError(TEST_CSV)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with TEST_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    saved = 0

    for row in rows:
        yolo_name = row.get("yolo_image_name")
        image_path = Path("data/processed/sai_split/test/images") / str(yolo_name)
        if not image_path.exists():
            image_path = Path("data/raw/sai_dataset") / row["image_path"]

        image = cv2.imread(str(image_path))

        if image is None:
            print(f"[WARN] Could not read: {image_path}")
            continue

        h, w = image.shape[:2]

        try:
            xmin = int(float(row["xmin"]))
            ymin = int(float(row["ymin"]))
            xmax = int(float(row["xmax"]))
            ymax = int(float(row["ymax"]))
        except (KeyError, ValueError) as exc:
            print(f"[WARN] Invalid bbox for {image_path}: {exc}")
            continue

        # Clamp coordinates safely.
        xmin = max(0, min(xmin, w - 1))
        ymin = max(0, min(ymin, h - 1))
        xmax = max(xmin + 1, min(xmax, w))
        ymax = max(ymin + 1, min(ymax, h))

        crop = image[ymin:ymax, xmin:xmax]

        if crop.size == 0:
            print(f"[WARN] Empty crop: {image_path}")
            continue

        output_name = f"{image_path.stem}.jpg"
        output_path = OUTPUT_DIR / output_name

        cv2.imwrite(str(output_path), crop)
        saved += 1

    print()
    print("=" * 55)
    print("GROUND-TRUTH PLATE CROP EXTRACTION")
    print("=" * 55)
    print(f"Input images : {len(rows)}")
    print(f"Crops saved  : {saved}")
    print(f"Output       : {OUTPUT_DIR.resolve()}")
    print("=" * 55)


if __name__ == "__main__":
    main()
