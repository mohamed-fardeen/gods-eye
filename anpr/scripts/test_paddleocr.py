from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import cv2
from paddleocr import PaddleOCR


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def normalize_text(text: str) -> str:
    text = str(text).upper()
    return re.sub(r"[^A-Z0-9]", "", text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="outputs/gt_plate_crops")
    parser.add_argument("--output", default="outputs/paddleocr_gt_baseline.csv")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_file = Path(args.output)

    if not input_dir.exists():
        raise FileNotFoundError(input_dir)

    images = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        raise RuntimeError("No plate crops found.")

    print("Loading PP-OCRv5 recognition model...")

    ocr = PaddleOCR(
        lang="en",
        use_gpu=False,
    )
 

    rows = []

    for index, image_path in enumerate(images, start=1):
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"[WARN] Could not read {image_path}")
            continue

        try:
            results = ocr.ocr(image, cls=False)

            if not results or not results[0]:
                prediction = ""
                confidence = 0.0
            else:
                # Pick the highest-confidence text line
                best = max(results[0], key=lambda x: x[1][1])
                prediction = normalize_text(best[1][0])
                confidence = float(best[1][1])

        except Exception as exc:
            print(f"[WARN] OCR failed for {image_path.name}: {exc}")
            prediction = ""
            confidence = 0.0

        rows.append({
            "image": image_path.name,
            "prediction": prediction,
            "ocr_confidence": confidence,
        })

        if index % 25 == 0 or index == len(images):
            print(f"Processed {index}/{len(images)}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "prediction", "ocr_confidence"])
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 55)
    print("PADDLEOCR BASELINE COMPLETE")
    print("=" * 55)
    print(f"Images processed : {len(rows)}")
    print(f"Results          : {output_file.resolve()}")
    print("=" * 55)


if __name__ == "__main__":
    main()
