"""
Dataset preparation (MILESTONE 4-5, 8, DATA SPLITTING section).

Responsibilities:
  1. Inventory the raw dataset (counts, formats found).
  2. Deduplicate near-identical images (perceptual hash) before splitting.
  3. Identity-aware split into train/val/test so augmented variants of the
     same source image never cross the split boundary.
  4. For plate crops with text labels: generate synthetic-degraded variants
     (blur/dark/glare/noise/compression/perspective/rain) for TRAIN ONLY —
     test data must stay clean-or-real, never train-style-augmented, or the
     benchmark stops meaning anything (see REAL VS SYNTHETIC CONDITIONS).

This is a template to run against whichever Indian plate dataset you've
downloaded into data/raw/ (e.g. a Roboflow "Indian license plate" detection
export, or IndianVehicleDataset-style plate+text sets). Adjust the
`load_raw_index()` function to match the actual folder layout you pulled.
"""

import argparse
import hashlib
import json
import os
import random
import shutil
from pathlib import Path

import cv2
import numpy as np

random.seed(42)


def phash(image_path: str, hash_size: int = 8) -> str:
    """Cheap perceptual hash for near-duplicate detection."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return hashlib.md5(image_path.encode()).hexdigest()
    resized = cv2.resize(img, (hash_size, hash_size))
    avg = resized.mean()
    bits = (resized > avg).flatten()
    return "".join("1" if b else "0" for b in bits)


def load_raw_index(raw_dir: str) -> list[dict]:
    """
    Returns a list of {"image_path", "label_path" (optional), "group_id"}.
    group_id = the base filename before any augmentation suffix, so that
    e.g. img001.jpg, img001_aug1.jpg map to the same group and stay together.
    ADAPT THIS to your actual downloaded dataset's structure.
    """
    records = []
    images_dir = Path(raw_dir) / "images"
    labels_dir = Path(raw_dir) / "labels"
    if not images_dir.exists():
        print(f"[prepare_dataset] WARNING: {images_dir} does not exist yet. "
              f"Download your Indian plate dataset into {raw_dir}/images (+ /labels) first.")
        return records

    for img_path in sorted(images_dir.glob("*.*")):
        base = img_path.stem.split("_aug")[0]
        label_path = labels_dir / (img_path.stem + ".txt")
        records.append({
            "image_path": str(img_path),
            "label_path": str(label_path) if label_path.exists() else None,
            "group_id": base,
        })
    return records


def dedupe(records: list[dict]) -> list[dict]:
    seen_hashes = {}
    kept = []
    dupes_removed = 0
    for r in records:
        h = phash(r["image_path"])
        if h in seen_hashes:
            dupes_removed += 1
            continue
        seen_hashes[h] = r["image_path"]
        kept.append(r)
    print(f"[prepare_dataset] Removed {dupes_removed} near-duplicate images.")
    return kept


def identity_aware_split(records: list[dict], train=0.8, val=0.1, test=0.1):
    groups = sorted(set(r["group_id"] for r in records))
    random.shuffle(groups)
    n = len(groups)
    n_train = int(n * train)
    n_val = int(n * val)
    train_groups = set(groups[:n_train])
    val_groups = set(groups[n_train:n_train + n_val])
    test_groups = set(groups[n_train + n_val:])

    split = {"train": [], "val": [], "test": []}
    for r in records:
        if r["group_id"] in train_groups:
            split["train"].append(r)
        elif r["group_id"] in val_groups:
            split["val"].append(r)
        else:
            split["test"].append(r)
    return split


def write_split(split: dict, out_dir: str):
    for name, records in split.items():
        img_out = Path(out_dir) / name / "images"
        lbl_out = Path(out_dir) / name / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for r in records:
            shutil.copy(r["image_path"], img_out / Path(r["image_path"]).name)
            if r["label_path"]:
                shutil.copy(r["label_path"], lbl_out / Path(r["label_path"]).name)
        print(f"[prepare_dataset] {name}: {len(records)} images")


def write_yolo_yaml(out_dir: str, class_names: list[str] = ("plate",)):
    yaml_content = f"""path: {os.path.abspath(out_dir)}
train: train/images
val: val/images
test: test/images
nc: {len(class_names)}
names: {list(class_names)}
"""
    yaml_path = Path(out_dir) / "data.yaml"
    yaml_path.write_text(yaml_content)
    print(f"[prepare_dataset] Wrote {yaml_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", default="data/raw/plate_detection")
    parser.add_argument("--out_dir", default="data/processed/plate_detection")
    args = parser.parse_args()

    records = load_raw_index(args.raw_dir)
    if not records:
        print("[prepare_dataset] No records found. Download a dataset first (see README build guide).")
        return

    records = dedupe(records)
    split = identity_aware_split(records)
    write_split(split, args.out_dir)
    write_yolo_yaml(args.out_dir)

    summary = {k: len(v) for k, v in split.items()}
    with open(Path(args.out_dir) / "split_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("[prepare_dataset] Done.", summary)


if __name__ == "__main__":
    main()
