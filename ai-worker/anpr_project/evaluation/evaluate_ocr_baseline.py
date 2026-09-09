from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from difflib import SequenceMatcher


def normalize(text: str) -> str:
    """Normalize only formatting; never substitute characters."""
    text = str(text).upper().strip()
    return re.sub(r"[^A-Z0-9]", "", text)


def levenshtein_distance(a: str, b: str) -> int:
    """Classic Levenshtein edit distance."""
    if a == b:
        return 0

    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i]

        for j, char_b in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (char_a != char_b)

            current.append(
                min(insert_cost, delete_cost, replace_cost)
            )

        previous = current

    return previous[-1]


def load_ground_truth(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required = {"image_path", "plate_text"}

        if not required.issubset(reader.fieldnames or set()):
            raise ValueError(
                f"{path} must contain columns: {required}"
            )

        data = {}

        for row in reader:
            filename = row.get("yolo_image_name") or Path(row["image_path"]).name

            data[filename] = {
                "plate_text": normalize(row["plate_text"]),
                "image_path": row["image_path"],
            }

        return data


def load_predictions(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def choose_prediction_for_image(
    rows: list[dict],
    ground_truth: str,
) -> dict | None:
    """
    Because one source image can produce multiple detected crops,
    select the candidate that is most plausible for the known GT.

    IMPORTANT:
    This function is used ONLY for diagnostic evaluation of the crop
    association problem. It is not permitted for the final benchmark
    because using GT text to choose a prediction would leak the answer.
    """

    if not rows:
        return None

    # For the honest benchmark, use the highest OCR-confidence candidate.
    return max(
        rows,
        key=lambda r: float(r.get("ocr_confidence", 0.0) or 0.0),
    )


def character_accuracy(gt: str, pred: str) -> float:
    if not gt:
        return 0.0

    # Sequence similarity is reported as a secondary diagnostic only.
    return SequenceMatcher(None, gt, pred).ratio()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ground-truth",
        default="data/processed/sai_split/test.csv",
    )

    parser.add_argument(
        "--predictions",
        default="outputs/ocr_baseline.csv",
    )

    parser.add_argument(
        "--output",
        default="outputs/ocr_baseline_evaluation.csv",
    )

    args = parser.parse_args()

    gt_path = Path(args.ground_truth)
    pred_path = Path(args.predictions)
    output_path = Path(args.output)

    if not gt_path.exists():
        raise FileNotFoundError(gt_path)

    if not pred_path.exists():
        raise FileNotFoundError(pred_path)

    ground_truth = load_ground_truth(gt_path)
    predictions = load_predictions(pred_path)

    # Group predictions by source image.
    grouped = {}

    for row in predictions:
        filename = Path(row["image"]).name

        # Extract original filename by removing our generated suffix.
        # Example:
        # original123_plate_0.jpg -> original123...
        if "_plate_" in filename:
            source_name = Path(filename.rsplit("_plate_", 1)[0]).stem
        else:
            source_name = Path(filename).stem

        grouped.setdefault(source_name, []).append(row)

    evaluation_rows = []

    exact_matches = 0
    total = 0
    nonempty_predictions = 0
    total_edit_distance = 0
    total_gt_chars = 0

    for filename, gt_info in ground_truth.items():

        gt = gt_info["plate_text"]

        stem = Path(filename).stem

        candidates = []

        for key, rows in grouped.items():
            if key == stem:
                candidates.extend(rows)

        if not candidates:
            # Detector failed to create a crop.
            prediction = ""
            confidence = 0.0
            candidate_count = 0
        else:
            # Honest selection rule: highest OCR confidence.
            best = max(
                candidates,
                key=lambda r: float(r.get("ocr_confidence", 0.0) or 0.0),
            )

            prediction = normalize(best.get("prediction", ""))
            confidence = float(
                best.get("ocr_confidence", 0.0) or 0.0
            )
            candidate_count = len(candidates)

        exact = prediction == gt and bool(prediction)

        edit_distance = levenshtein_distance(gt, prediction)

        if exact:
            exact_matches += 1

        if prediction:
            nonempty_predictions += 1

        total_edit_distance += edit_distance
        total_gt_chars += len(gt)

        evaluation_rows.append(
            {
                "image": filename,
                "ground_truth": gt,
                "prediction": prediction,
                "ocr_confidence": f"{confidence:.6f}",
                "candidate_count": candidate_count,
                "exact_match": int(exact),
                "edit_distance": edit_distance,
                "character_similarity": f"{character_accuracy(gt, prediction):.6f}",
            }
        )

        total += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "ground_truth",
                "prediction",
                "ocr_confidence",
                "candidate_count",
                "exact_match",
                "edit_distance",
                "character_similarity",
            ],
        )

        writer.writeheader()
        writer.writerows(evaluation_rows)

    exact_accuracy = exact_matches / total if total else 0.0
    coverage = nonempty_predictions / total if total else 0.0
    cer = total_edit_distance / total_gt_chars if total_gt_chars else 0.0

    print()
    print("=" * 60)
    print("OCR BASELINE — EXACT MATCH EVALUATION")
    print("=" * 60)

    print(f"Ground-truth plates       : {total}")
    print(f"Non-empty OCR             : {nonempty_predictions}")
    print(f"OCR coverage              : {coverage * 100:.2f}%")
    print(f"Exact plate matches       : {exact_matches}")
    print(f"Exact-match accuracy      : {exact_accuracy * 100:.2f}%")
    print(f"Character error rate      : {cer * 100:.2f}%")
    print(f"Evaluation CSV            : {output_path.resolve()}")
    print("=" * 60)

    print("\nFirst incorrect predictions:")

    shown = 0

    for row in evaluation_rows:
        if row["exact_match"] == "0":
            print(
                f"GT={row['ground_truth']:<15} "
                f"PRED={row['prediction']:<15} "
                f"conf={row['ocr_confidence']}"
            )

            shown += 1

            if shown >= 20:
                break


if __name__ == "__main__":
    main()
