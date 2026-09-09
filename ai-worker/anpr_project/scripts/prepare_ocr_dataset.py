from __future__ import annotations

import csv
from pathlib import Path

import cv2


INPUT_ROOT  = Path("data/processed/sai_split")
IMAGE_ROOT  = Path("data/raw")          # CSV image_path values are relative to here
OUTPUT_ROOT = Path("data/processed/ocr_recognition")


def prepare_split(split: str) -> None:
    csv_path = INPUT_ROOT / f"{split}.csv"
    image_output = OUTPUT_ROOT / split / "images"
    label_output = OUTPUT_ROOT / split / f"{split}.txt"

    image_output.mkdir(parents=True, exist_ok=True)

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    written = 0
    skipped = 0

    with label_output.open(
        "w",
        encoding="utf-8",
    ) as label_file:

        for index, row in enumerate(rows):

            image_path = Path(row["image_path"])
            # CSV paths are relative to data/raw/ on this machine
            if not image_path.exists():
                image_path = IMAGE_ROOT / image_path
            image = cv2.imread(str(image_path))

            if image is None:
                skipped += 1
                continue

            try:
                xmin = int(float(row["xmin"]))
                ymin = int(float(row["ymin"]))
                xmax = int(float(row["xmax"]))
                ymax = int(float(row["ymax"]))
            except (ValueError, KeyError):
                skipped += 1
                continue

            h, w = image.shape[:2]

            xmin = max(0, min(xmin, w - 1))
            ymin = max(0, min(ymin, h - 1))
            xmax = max(xmin + 1, min(xmax, w))
            ymax = max(ymin + 1, min(ymax, h))

            crop = image[ymin:ymax, xmin:xmax]

            if crop.size == 0:
                skipped += 1
                continue

            plate_text = str(row["plate_text"]).strip()

            if not plate_text:
                skipped += 1
                continue

            output_name = f"{index:06d}.jpg"
            output_image = image_output / output_name

            ok = cv2.imwrite(str(output_image), crop)

            if not ok:
                skipped += 1
                continue

            # PaddleOCR recognition dataset format:
            # image_path<TAB>label
            label_file.write(
                f"{output_image.as_posix()}\t{plate_text}\n"
            )

            written += 1

    print()
    print(f"{split.upper()} OCR DATASET")
    print("-" * 50)
    print(f"Input rows : {len(rows)}")
    print(f"Written    : {written}")
    print(f"Skipped    : {skipped}")
    print(f"Images     : {image_output.resolve()}")
    print(f"Labels     : {label_output.resolve()}")


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    prepare_split("train")
    prepare_split("val")

    print()
    print("=" * 60)
    print("OCR DATASET PREPARATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
