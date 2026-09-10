"""
Evaluation system (MILESTONE 19-21, EXACT EVALUATION SYSTEM section).

Never fabricates numbers: this script only reports what's actually in
predictions.csv vs ground_truth.csv. If a file is missing or empty for a
condition, that condition is reported as "NO DATA" rather than silently
skipped or invented.

Inputs (place in evaluation/):
  ground_truth.csv : track_id, true_plate, condition, source_type
                      (source_type = "real" | "synthetic")
  predictions.csv  : track_id, predicted_plate, confidence, status,
                      num_observations, evidence_frame_ids

Usage:
  python evaluation/evaluate.py --gt evaluation/ground_truth.csv --pred evaluation/predictions.csv
"""

import argparse
import csv
from collections import defaultdict, Counter


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def char_accuracy(true_s: str, pred_s: str) -> float:
    if not true_s:
        return 0.0
    if pred_s is None:
        pred_s = ""
    matches = sum(1 for a, b in zip(true_s, pred_s) if a == b)
    return matches / max(len(true_s), len(pred_s), 1)


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = curr
    return prev[-1]


def evaluate(gt_rows, pred_rows):
    pred_by_track = {r["track_id"]: r for r in pred_rows}

    condition_totals = defaultdict(lambda: {"exact": 0, "total": 0, "source_type": set()})
    char_acc_values = []
    cer_values = []
    unreadable_count = 0
    confidence_values = []
    confusions = Counter()

    for gt in gt_rows:
        track_id = gt["track_id"]
        condition = gt.get("condition", "unspecified")
        source_type = gt.get("source_type", "unspecified")
        true_plate = gt["true_plate"].strip().upper()

        pred = pred_by_track.get(track_id)
        pred_plate = (pred["predicted_plate"].strip().upper() if pred and pred.get("predicted_plate") else "")
        status = pred.get("status", "MISSING") if pred else "MISSING"

        condition_totals[condition]["total"] += 1
        condition_totals[condition]["source_type"].add(source_type)

        if status == "UNREADABLE" or not pred_plate:
            unreadable_count += 1
        else:
            if pred_plate == true_plate:
                condition_totals[condition]["exact"] += 1
            char_acc_values.append(char_accuracy(true_plate, pred_plate))
            cer_values.append(levenshtein(true_plate, pred_plate) / max(len(true_plate), 1))
            for a, b in zip(true_plate, pred_plate):
                if a != b:
                    confusions[(a, b)] += 1

        if pred and pred.get("confidence"):
            try:
                confidence_values.append(float(pred["confidence"]))
            except ValueError:
                pass

    return {
        "condition_totals": condition_totals,
        "char_acc_values": char_acc_values,
        "cer_values": cer_values,
        "unreadable_count": unreadable_count,
        "confidence_values": confidence_values,
        "confusions": confusions,
        "n_total": len(gt_rows),
    }


def print_report(results):
    print("=" * 48)
    print("TEMPORAL QUALITY-AWARE ANPR EVALUATION")
    print("=" * 48)
    print(f"{'Condition':<20}{'Source':<12}{'Exact Match':>12}")
    print("-" * 48)

    total_exact = 0
    total_n = 0
    for condition, data in sorted(results["condition_totals"].items()):
        exact, total = data["exact"], data["total"]
        total_exact += exact
        total_n += total
        pct = (exact / total * 100) if total > 0 else float("nan")
        source_label = "/".join(sorted(data["source_type"])) or "unspecified"
        pct_str = f"{pct:.1f}%" if total > 0 else "NO DATA"
        print(f"{condition:<20}{source_label:<12}{pct_str:>12}")

    print("-" * 48)
    overall = (total_exact / total_n * 100) if total_n > 0 else float("nan")
    print(f"{'Overall':<32}{overall:>11.1f}%" if total_n > 0 else f"{'Overall':<32}{'NO DATA':>12}")
    print()

    if results["char_acc_values"]:
        mean_char_acc = sum(results["char_acc_values"]) / len(results["char_acc_values"])
        print(f"Mean character accuracy (non-unreadable): {mean_char_acc*100:.1f}%")
    if results["cer_values"]:
        mean_cer = sum(results["cer_values"]) / len(results["cer_values"])
        print(f"Mean character error rate (non-unreadable): {mean_cer*100:.1f}%")

    print(f"Unreadable / rejected: {results['unreadable_count']} / {results['n_total']} "
          f"({results['unreadable_count']/max(results['n_total'],1)*100:.1f}%)")

    if results["confidence_values"]:
        cv = results["confidence_values"]
        print(f"Confidence distribution: min={min(cv):.2f} mean={sum(cv)/len(cv):.2f} max={max(cv):.2f}")

    if results["confusions"]:
        print("\nTop character confusions (true -> predicted):")
        for (a, b), n in results["confusions"].most_common(10):
            print(f"  {a} -> {b}: {n}")

    print("\nNOTE: 'synthetic' source_type rows simulate conditions on clean images and")
    print("must NOT be reported as real-world adverse-condition performance.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gt", default="evaluation/ground_truth.csv")
    parser.add_argument("--pred", default="evaluation/predictions.csv")
    args = parser.parse_args()

    gt_rows = load_csv(args.gt)
    pred_rows = load_csv(args.pred)
    if not gt_rows:
        print(f"No ground truth rows in {args.gt} — nothing to evaluate. "
              "Fill this in as you label test-set outcomes.")
    else:
        results = evaluate(gt_rows, pred_rows)
        print_report(results)
