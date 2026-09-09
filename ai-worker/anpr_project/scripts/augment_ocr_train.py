"""
augment_ocr_train.py
====================
Expand the OCR recognition training set with realistic CCTV degradations.

Strategy
--------
* Original clean crops  -> kept as-is (already written by prepare_ocr_dataset.py)
* 7 single-degradation  variants per image: blur, dark, glare, noise,
  compression, perspective, rain
* 2 combined degradations per image: (blur+dark) and (noise+compression)
  to mimic the most common CCTV failure modes

Total expansion factor: 1 (clean) + 7 (single) + 2 (combined) = 10x
But we write ONLY the 9 degraded variants here so the caller can keep the
clean labels file intact.  The final labels file merges both.

Output
------
data/processed/ocr_recognition/train/aug_images/   <- degraded crops
data/processed/ocr_recognition/train/aug.txt        <- tab-separated labels
data/processed/ocr_recognition/train/train_full.txt <- clean + aug merged

Usage
-----
python scripts/augment_ocr_train.py
"""

from __future__ import annotations

import random
from pathlib import Path

import cv2
import numpy as np


random.seed(42)
np.random.seed(42)

# -- source / destination paths ------------------------------------------------
TRAIN_ROOT   = Path("data/processed/ocr_recognition/train")
CLEAN_LABELS = TRAIN_ROOT / "train.txt"
AUG_IMAGES   = TRAIN_ROOT / "aug_images"
AUG_LABELS   = TRAIN_ROOT / "aug.txt"
FULL_LABELS  = TRAIN_ROOT / "train_full.txt"


# -- degradation primitives ----------------------------------------------------

def add_motion_blur(img: np.ndarray) -> np.ndarray:
    k = random.choice([5, 7, 9, 11])
    kernel = np.zeros((k, k), dtype=np.float32)
    kernel[(k - 1) // 2, :] = 1.0 / k
    return cv2.filter2D(img, -1, kernel)


def darken(img: np.ndarray) -> np.ndarray:
    f = random.uniform(0.25, 0.55)
    return np.clip(img.astype(np.float32) * f, 0, 255).astype(np.uint8)


def add_glare(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    overlay = img.copy()
    cx = random.randint(0, w - 1)
    cy = random.randint(0, h - 1)
    radius = random.randint(max(1, w // 4), max(2, w // 2))
    cv2.circle(overlay, (cx, cy), radius, (255, 255, 255), -1)
    return cv2.addWeighted(overlay, 0.35, img, 0.65, 0)


def add_noise(img: np.ndarray) -> np.ndarray:
    sigma = random.uniform(8, 20)
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def jpeg_compress(img: np.ndarray) -> np.ndarray:
    quality = random.randint(15, 40)
    ok, enc = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR) if ok else img


def perspective_warp(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    strength = 0.12
    jitter = w * strength
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([
        [random.uniform(0, jitter),     random.uniform(0, jitter)],
        [w - random.uniform(0, jitter), random.uniform(0, jitter)],
        [w - random.uniform(0, jitter), h - random.uniform(0, jitter)],
        [random.uniform(0, jitter),     h - random.uniform(0, jitter)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)


def rain_streaks(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    overlay = img.copy()
    for _ in range(int(w * h * 0.0008)):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        length = random.randint(5, 12)
        cv2.line(overlay, (x, y), (x - 2, y + length), (200, 200, 200), 1)
    blended = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
    return cv2.GaussianBlur(blended, (3, 3), 0)


# -- named single degradations -------------------------------------------------
SINGLE_DEGRADATIONS: dict = {
    "blur":        add_motion_blur,
    "dark":        darken,
    "glare":       add_glare,
    "noise":       add_noise,
    "compression": jpeg_compress,
    "perspective": perspective_warp,
    "rain":        rain_streaks,
}

# -- combined degradations (ordered pipelines) ---------------------------------
# Targets the two most damaging real-world combos
COMBINED_DEGRADATIONS: dict = {
    "blur_dark":         [add_motion_blur, darken],
    "noise_compression": [add_noise, jpeg_compress],
}


def apply_pipeline(img: np.ndarray, fns: list) -> np.ndarray:
    for fn in fns:
        img = fn(img.copy())
    return img


# -- main ----------------------------------------------------------------------

def main() -> None:
    if not CLEAN_LABELS.exists():
        raise FileNotFoundError(
            f"{CLEAN_LABELS} not found. "
            "Run scripts/prepare_ocr_dataset.py first."
        )

    AUG_IMAGES.mkdir(parents=True, exist_ok=True)

    # Read clean label file
    clean_lines = [
        line.strip()
        for line in CLEAN_LABELS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    print(f"Clean training samples : {len(clean_lines)}")

    aug_lines: list = []
    skipped = 0
    written = 0

    for line in clean_lines:
        parts = line.split("\t", 1)
        if len(parts) != 2:
            skipped += 1
            continue

        image_posix, label = parts
        img = cv2.imread(image_posix)

        if img is None:
            skipped += 1
            continue

        stem = Path(image_posix).stem

        # 7 single-degradation variants
        for tag, fn in SINGLE_DEGRADATIONS.items():
            degraded = fn(img.copy())
            out_path = AUG_IMAGES / f"{stem}_{tag}.jpg"
            if cv2.imwrite(str(out_path), degraded):
                aug_lines.append(f"{out_path.as_posix()}\t{label}")
                written += 1
            else:
                skipped += 1

        # 2 combined-degradation variants
        for tag, pipeline in COMBINED_DEGRADATIONS.items():
            degraded = apply_pipeline(img.copy(), pipeline)
            out_path = AUG_IMAGES / f"{stem}_{tag}.jpg"
            if cv2.imwrite(str(out_path), degraded):
                aug_lines.append(f"{out_path.as_posix()}\t{label}")
                written += 1
            else:
                skipped += 1

    # Write aug-only labels
    AUG_LABELS.write_text("\n".join(aug_lines) + "\n", encoding="utf-8")

    # Merge clean + aug into train_full.txt
    merged = clean_lines + aug_lines
    FULL_LABELS.write_text("\n".join(merged) + "\n", encoding="utf-8")

    print()
    print("=" * 60)
    print("OCR AUGMENTATION COMPLETE")
    print("=" * 60)
    print(f"Clean samples          : {len(clean_lines)}")
    print(f"Augmented variants     : {written}")
    print(f"Skipped                : {skipped}")
    print(f"Total (train_full.txt) : {len(merged)}")
    print(f"Expansion factor       : {len(merged) / max(len(clean_lines), 1):.1f}x")
    print(f"Aug images             : {AUG_IMAGES.resolve()}")
    print(f"Aug labels             : {AUG_LABELS.resolve()}")
    print(f"Merged labels          : {FULL_LABELS.resolve()}")
    print("=" * 60)
    print()
    print("Degradations applied per image:")
    for tag in list(SINGLE_DEGRADATIONS) + list(COMBINED_DEGRADATIONS):
        print(f"  * {tag}")


if __name__ == "__main__":
    main()
