"""
Generate synthetic-degraded variants of clean plate crops for OCR
fine-tuning / robustness training (MILESTONE 8, DATA STRATEGY).

IMPORTANT: run this ONLY on the train split. Test data must remain real or
untouched-clean so evaluation reports which results are real-condition vs
synthetic-condition (see REAL VS SYNTHETIC CONDITIONS).

Usage:
  python scripts/synthetic_degrade.py --in_dir data/processed/plate_detection/train/crops --out_dir data/processed/ocr_train
"""

import argparse
import random
from pathlib import Path

import cv2
import numpy as np

random.seed(42)


def add_motion_blur(img, kernel_size=None):
    k = kernel_size or random.choice([5, 7, 9, 11])
    kernel = np.zeros((k, k))
    kernel[(k - 1) // 2, :] = np.ones(k)
    kernel /= k
    return cv2.filter2D(img, -1, kernel)


def darken(img, factor=None):
    f = factor or random.uniform(0.25, 0.55)
    return np.clip(img.astype(np.float32) * f, 0, 255).astype(np.uint8)


def add_glare(img):
    h, w = img.shape[:2]
    overlay = img.copy()
    cx, cy = random.randint(0, w), random.randint(0, h)
    radius = random.randint(w // 4, w // 2)
    cv2.circle(overlay, (cx, cy), radius, (255, 255, 255), -1)
    return cv2.addWeighted(overlay, 0.35, img, 0.65, 0)


def add_noise(img, sigma=None):
    s = sigma or random.uniform(8, 20)
    noise = np.random.normal(0, s, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def jpeg_compress(img, quality=None):
    q = quality or random.randint(15, 40)
    ok, enc = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, q])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR) if ok else img


def perspective_warp(img, strength=0.12):
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    jitter = w * strength
    dst = np.float32([
        [random.uniform(0, jitter), random.uniform(0, jitter)],
        [w - random.uniform(0, jitter), random.uniform(0, jitter)],
        [w - random.uniform(0, jitter), h - random.uniform(0, jitter)],
        [random.uniform(0, jitter), h - random.uniform(0, jitter)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)


def rain_streaks(img):
    h, w = img.shape[:2]
    overlay = img.copy()
    for _ in range(int(w * h * 0.0008)):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        length = random.randint(5, 12)
        cv2.line(overlay, (x, y), (x - 2, y + length), (200, 200, 200), 1)
    blended = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
    return cv2.GaussianBlur(blended, (3, 3), 0)


DEGRADATIONS = {
    "blur": add_motion_blur,
    "dark": darken,
    "glare": add_glare,
    "noise": add_noise,
    "compression": jpeg_compress,
    "perspective": perspective_warp,
    "rain": rain_streaks,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--variants_per_image", type=int, default=3,
                         help="how many random degradations to apply per source image, plus the clean original")
    args = parser.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    image_paths = list(in_dir.glob("*.jpg")) + list(in_dir.glob("*.png"))
    if not image_paths:
        print(f"[synthetic_degrade] No images found in {in_dir}. Run prepare_dataset.py first.")
        return

    names = list(DEGRADATIONS.keys())
    count = 0
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        cv2.imwrite(str(out_dir / f"{img_path.stem}_clean.jpg"), img)
        count += 1

        chosen = random.sample(names, k=min(args.variants_per_image, len(names)))
        for tag in chosen:
            degraded = DEGRADATIONS[tag](img.copy())
            cv2.imwrite(str(out_dir / f"{img_path.stem}_{tag}.jpg"), degraded)
            count += 1

    print(f"[synthetic_degrade] Wrote {count} images ({len(image_paths)} sources) to {out_dir}")


if __name__ == "__main__":
    main()
