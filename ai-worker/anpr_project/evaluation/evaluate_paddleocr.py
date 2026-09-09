from __future__ import annotations

import csv
import re
from pathlib import Path


GT_FILE = Path("data/processed/sai_split/test.csv")
PRED_FILE = Path("outputs/paddleocr_gt_baseline.csv")


def normalize(text: str) -> str:
    text = str(text).upper()
    return re.sub(r"[^A-Z0-9]", "", text)


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0

    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, ca in enumerate(a, 1):
        current = [i]

        for j, cb in enumerate(b, 1):
            current.append(
                min(
                    current[j - 1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (ca != cb),
                )
            )

        previous = current

    return previous[-1]


def main() -> None:

    with GT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        gt_rows = list(csv.DictReader(f))

    gt = {
        Path(row.get("yolo_image_name") or row["image_path"]).stem:
        normalize(row["plate_text"])
        for row in gt_rows
    }

    with PRED_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        predictions = list(csv.DictReader(f))

    total = 0
    exact = 0
    nonempty = 0
    edit_distance = 0
    gt_characters = 0

    incorrect = []

    for row in predictions:

        stem = Path(row["image"]).stem

        if stem not in gt:
            continue

        ground_truth = gt[stem]
        prediction = normalize(row["prediction"])

        total += 1

        if prediction:
            nonempty += 1

        distance = levenshtein(
            ground_truth,
            prediction,
        )

        edit_distance += distance
        gt_characters += len(ground_truth)

        if prediction == ground_truth:
            exact += 1
        else:
            incorrect.append(
                (
                    ground_truth,
                    prediction,
                    float(row["ocr_confidence"]),
                )
            )

    exact_accuracy = (
        exact / total
        if total
        else 0.0
    )

    coverage = (
        nonempty / total
        if total
        else 0.0
    )

    cer = (
        edit_distance / gt_characters
        if gt_characters
        else 0.0
    )

    print()
    print("=" * 60)
    print("PADDLEOCR — GROUND-TRUTH CROP EVALUATION")
    print("=" * 60)

    print(f"Images evaluated       : {total}")
    print(f"Non-empty OCR          : {nonempty}")
    print(f"OCR coverage           : {coverage * 100:.2f}%")
    print(f"Exact matches          : {exact}")
    print(f"Exact-match accuracy   : {exact_accuracy * 100:.2f}%")
    print(f"Character error rate   : {cer * 100:.2f}%")

    print("=" * 60)

    print("\nIncorrect predictions:")

    for gt_text, pred_text, confidence in incorrect[:25]:

        print(
            f"GT={gt_text:<15} "
            f"PRED={pred_text:<15} "
            f"CONF={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
