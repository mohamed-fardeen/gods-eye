"""
Lightweight preprocessing: perspective correction + enhancement.

Deliberately NOT a learned restoration model (per RULE 3 / MILESTONE 13-14):
just classical OpenCV operations that are fast, explainable, and cheap to
disable per-path if evaluation shows they hurt OCR (see FALLBACK STRATEGY).
"""

import cv2
import numpy as np


def correct_perspective(crop_bgr: np.ndarray, quad: np.ndarray | None = None) -> np.ndarray:
    """
    If `quad` (4 corner points of the plate, from the detector/segmenter) is
    given, warp to a fronto-parallel rectangle. If not given, fall back to a
    lightweight deskew based on the crop's minimum-area rectangle — cheaper
    than requiring 4-point plate corner annotations, which most detection
    datasets don't provide (axis-aligned boxes only).
    """
    if quad is not None and quad.shape == (4, 2):
        rect = _order_points(quad.astype("float32"))
        (tl, tr, br, bl) = rect
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array(
            [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
            dtype="float32",
        )
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(crop_bgr, M, (maxWidth, maxHeight))

    # Fallback: deskew via minAreaRect on the largest contour of edges.
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    coords = cv2.findNonZero(edges)
    if coords is None:
        return crop_bgr
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < 1.0:  # not worth rotating
        return crop_bgr
    (h, w) = crop_bgr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(crop_bgr, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def enhance_for_ocr(crop_bgr: np.ndarray, upscale_to_height: int = 64) -> np.ndarray:
    """
    Cheap, general-purpose enhancement pipeline tuned for plate OCR:
    grayscale -> CLAHE (local contrast, helps glare/shadow) -> mild denoise
    -> unsharp mask -> upscale to a consistent height (OCR models are
    sensitive to character pixel height).

    Each stage is intentionally isolated so any one can be toggled off if
    ablation shows it hurts a given condition (see FALLBACK STRATEGY).
    """
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_boosted = clahe.apply(gray)

    denoised = cv2.fastNlMeansDenoising(contrast_boosted, h=7, templateWindowSize=7, searchWindowSize=21)

    blurred = cv2.GaussianBlur(denoised, (0, 0), sigmaX=1.0)
    sharpened = cv2.addWeighted(denoised, 1.5, blurred, -0.5, 0)

    h, w = sharpened.shape[:2]
    if h < upscale_to_height:
        scale = upscale_to_height / h
        sharpened = cv2.resize(
            sharpened, (int(w * scale), upscale_to_height), interpolation=cv2.INTER_CUBIC
        )

    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)  # most OCR engines expect 3-channel


if __name__ == "__main__":
    fake = np.random.randint(0, 255, (40, 150, 3), dtype=np.uint8)
    out = enhance_for_ocr(fake)
    print("Self-test enhance output shape:", out.shape)
