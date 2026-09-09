from __future__ import annotations

import csv
import re
from pathlib import Path


GT_FILE = Path("data/processed/sai_split/test.csv")
OCR_FILE = Path("outputs/ocr_gt_crop.csv")


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

    ground_truth = {
        Path(row.get("yolo_image_name") or row["image_path"]).stem: normalize(row["plate_text"])
        for row in gt_rows
    }

    with OCR_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        predictions = list(csv.DictReader(f))

    exact = 0
    nonempty = 0
    total = 0
    edit_distance = 0
    gt_characters = 0

    incorrect = []

    for row in predictions:
        stem = Path(row["image"]).stem

        if stem not in ground_truth:
            continue

        gt = ground_truth[stem]
        pred = normalize(row.get("prediction", ""))

        total += 1

        if pred:
            nonempty += 1

        distance = levenshtein(gt, pred)

        edit_distance += distance
        gt_characters += len(gt)

        if pred == gt and pred:
            exact += 1
        else:
            incorrect.append(
                (
                    gt,
                    pred,
                    float(row.get("ocr_confidence", 0) or 0),
                )
            )

    accuracy = exact / total if total else 0
    coverage = nonempty / total if total else 0
    cer = edit_distance / gt_characters if gt_characters else 0

    print()
    print("=" * 60)
    print("EASYOCR ON GROUND-TRUTH PLATE CROPS")
    print("=" * 60)
    print(f"Evaluated images       : {total}")
    print(f"Non-empty OCR          : {nonempty}")
    print(f"OCR coverage           : {coverage * 100:.2f}%")
    print(f"Exact plate matches    : {exact}")
    print(f"Exact-match accuracy   : {accuracy * 100:.2f}%")
    print(f"Character error rate   : {cer * 100:.2f}%")
    print("=" * 60)

    print("\nFirst incorrect results:")

    for gt, pred, confidence in incorrect[:25]:
        print(
            f"GT={gt:<15} "
            f"PRED={pred:<15} "
            f"CONF={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
