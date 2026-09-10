from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import cv2
import easyocr


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def normalize_text(text: str) -> str:
    """
    Normalize OCR output for license-plate comparison.

    We intentionally do NOT perform character substitution such as:
    O -> 0 or I -> 1 because that would artificially improve accuracy.
    """
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def run_ocr(
    input_dir: str,
    output_csv: str,
    gpu: bool = True,
) -> None:
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_path}")

    images = sorted(
        p
        for p in input_path.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        raise FileNotFoundError(f"No image files found in: {input_path}")

    print("Loading EasyOCR...")
    print(f"GPU enabled: {gpu}")

    reader = easyocr.Reader(
        ["en"],
        gpu=gpu,
        verbose=True,
    )

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for index, image_path in enumerate(images, start=1):
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"[WARN] Could not read: {image_path}")
            continue

        try:
            results = reader.readtext(
                image,
                detail=1,
                paragraph=False,
                batch_size=1,
                mag_ratio=1.5,
            )
        except Exception as exc:
            print(f"[WARN] OCR failed for {image_path}: {exc}")
            continue

        candidates = []

        for bbox, text, confidence in results:
            normalized = normalize_text(text)

            if normalized:
                candidates.append(
                    {
                        "raw_text": text,
                        "text": normalized,
                        "ocr_confidence": float(confidence),
                    }
                )

        # Select the highest-confidence candidate.
        if candidates:
            candidates.sort(
                key=lambda x: x["ocr_confidence"],
                reverse=True,
            )

            best = candidates[0]

            prediction = best["text"]
            confidence = best["ocr_confidence"]
            raw_text = best["raw_text"]

        else:
            prediction = ""
            confidence = 0.0
            raw_text = ""

        rows.append(
            {
                "image": image_path.name,
                "image_path": str(image_path),
                "prediction": prediction,
                "raw_prediction": raw_text,
                "ocr_confidence": confidence,
                "num_candidates": len(candidates),
            }
        )

        if index % 25 == 0 or index == len(images):
            print(
                f"Processed {index}/{len(images)} | "
                f"recognized={sum(bool(r['prediction']) for r in rows)}"
            )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "image_path",
                "prediction",
                "raw_prediction",
                "ocr_confidence",
                "num_candidates",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 50)
    print("OCR BASELINE COMPLETE")
    print("=" * 50)
    print(f"Images processed : {len(rows)}")
    print(
        f"Non-empty OCR    : "
        f"{sum(bool(r['prediction']) for r in rows)}"
    )
    print(f"Results saved    : {output_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="outputs/test_plate_crops",
        help="Directory containing plate crops.",
    )

    parser.add_argument(
        "--output",
        default="outputs/ocr_baseline.csv",
        help="Output CSV path.",
    )

    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU instead of GPU.",
    )

    args = parser.parse_args()

    run_ocr(
        input_dir=args.input,
        output_csv=args.output,
        gpu=not args.cpu,
    )


if __name__ == "__main__":
    main()
