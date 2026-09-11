"""
Plate observation quality scoring.

Given a plate crop (BGR numpy array), returns a normalized quality score
in [0, 1] combining sharpness, brightness, contrast, and relative size.

Design notes:
- Sharpness uses variance of Laplacian (fast, well-validated proxy for blur).
- Brightness/contrast use simple statistics on the grayscale histogram.
- Size score rewards larger, more legible crops (small plates -> low quality
  regardless of sharpness, since character strokes may be sub-pixel).
- All sub-scores are combined with weights tuned for "does this crop help
  OCR read the plate", not generic image aesthetics.
"""

from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class QualityBreakdown:
    sharpness: float
    brightness: float
    contrast: float
    size: float
    overall: float


# Empirically reasonable defaults for CCTV plate crops; tune after
# looking at real score distributions in evaluation/ (see MILESTONE 12/22).
LAPLACIAN_SATURATION = 400.0   # var(Laplacian) at/above this -> sharpness=1.0
MIN_USABLE_WIDTH_PX = 60        # plate crops narrower than this are low quality
IDEAL_WIDTH_PX = 180            # crops at/above this get full size score

WEIGHTS = {
    "sharpness": 0.45,
    "brightness": 0.15,
    "contrast": 0.15,
    "size": 0.25,
}


def _sharpness_score(gray: np.ndarray) -> float:
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(np.clip(lap_var / LAPLACIAN_SATURATION, 0.0, 1.0))


def _brightness_score(gray: np.ndarray) -> float:
    mean = gray.mean()  # 0-255
    # Penalize both underexposed (near 0) and blown-out (near 255) crops.
    # Peak score at mean ~ 120-140.
    ideal = 130.0
    dist = abs(mean - ideal) / ideal
    return float(np.clip(1.0 - dist, 0.0, 1.0))


def _contrast_score(gray: np.ndarray) -> float:
    std = gray.std()  # low std = washed out / foggy / glare
    return float(np.clip(std / 60.0, 0.0, 1.0))


def _size_score(width_px: int) -> float:
    if width_px <= MIN_USABLE_WIDTH_PX:
        return 0.0
    if width_px >= IDEAL_WIDTH_PX:
        return 1.0
    return (width_px - MIN_USABLE_WIDTH_PX) / (IDEAL_WIDTH_PX - MIN_USABLE_WIDTH_PX)


def score_plate_crop(crop_bgr: np.ndarray) -> QualityBreakdown:
    """
    crop_bgr: HxWx3 BGR image of just the plate region (already cropped
    from the full frame using the detector bbox).
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return QualityBreakdown(0.0, 0.0, 0.0, 0.0, 0.0)

    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    sharpness = _sharpness_score(gray)
    brightness = _brightness_score(gray)
    contrast = _contrast_score(gray)
    size = _size_score(w)

    overall = (
        WEIGHTS["sharpness"] * sharpness
        + WEIGHTS["brightness"] * brightness
        + WEIGHTS["contrast"] * contrast
        + WEIGHTS["size"] * size
    )
    return QualityBreakdown(sharpness, brightness, contrast, size, float(np.clip(overall, 0.0, 1.0)))


if __name__ == "__main__":
    # Quick self-test with a synthetic crop so this file is runnable standalone.
    fake = np.random.randint(0, 255, (40, 150, 3), dtype=np.uint8)
    result = score_plate_crop(fake)
    print("Self-test quality breakdown:", result)
