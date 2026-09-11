"""
OCR engine wrapper.

Primary: PaddleOCR (PP-OCRv4 mobile det+rec) — general-purpose, pretrained,
strong out of the box, easy to fine-tune later if MILESTONE 9 shows it's
worth it.

Fallback / comparison: fast-plate-ocr — a lightweight model built
specifically for already-cropped plate images (no text detection needed,
just recognition), useful as Baseline comparison and as a fast fallback if
PaddleOCR's detection stage struggles on tiny crops.

Both return a list of (text, confidence) candidates so the fusion stage
(app/fusion) always has something to weight, even on a bad read.
"""

from dataclasses import dataclass
import re

try:
    from paddleocr import PaddleOCR
    _PADDLE_AVAILABLE = True
except ImportError:
    _PADDLE_AVAILABLE = False

try:
    from fast_plate_ocr import ONNXPlateRecognizer
    _FAST_PLATE_AVAILABLE = True
except ImportError:
    _FAST_PLATE_AVAILABLE = False


@dataclass
class OCRCandidate:
    text: str
    confidence: float
    engine: str


_ALNUM_RE = re.compile(r"[^A-Z0-9]")


def _clean(text: str) -> str:
    return _ALNUM_RE.sub("", text.upper())


class OCREngine:
    def __init__(self, engine: str = "paddle", use_gpu: bool = True):
        """
        engine: "paddle" | "fast_plate" | "both"
        """
        self.engine = engine
        self._paddle = None
        self._fast_plate = None

        if engine in ("paddle", "both"):
            if not _PADDLE_AVAILABLE:
                raise ImportError("PaddleOCR not installed. Run: pip install paddleocr")
            # rec-only, no angle classifier (we handle rotation in preprocessing)
            # and no detection stage since input is already a tight plate crop.
            self._paddle = PaddleOCR(
                use_angle_cls=False,
                lang="en",
                use_gpu=use_gpu,
                show_log=False,
                det=False,  # crop already localizes the plate; skip re-detection
            )

        if engine in ("fast_plate", "both"):
            if not _FAST_PLATE_AVAILABLE:
                raise ImportError("fast-plate-ocr not installed. Run: pip install fast-plate-ocr")
            self._fast_plate = ONNXPlateRecognizer("cct-xs-v1-global-model")

    def read(self, crop_bgr) -> list[OCRCandidate]:
        candidates: list[OCRCandidate] = []

        if self._paddle is not None:
            try:
                result = self._paddle.ocr(crop_bgr, cls=False)
                if result and result[0]:
                    for line in result[0]:
                        text, conf = line[1]
                        cleaned = _clean(text)
                        if cleaned:
                            candidates.append(OCRCandidate(cleaned, float(conf), "paddle"))
            except Exception:
                pass  # a single bad frame should never crash the pipeline

        if self._fast_plate is not None:
            try:
                texts = self._fast_plate.run(crop_bgr)
                for text in texts:
                    cleaned = _clean(text)
                    if cleaned:
                        # fast-plate-ocr doesn't expose per-char confidence in
                        # this call; use a fixed prior, fusion will still
                        # weight it by crop quality.
                        candidates.append(OCRCandidate(cleaned, 0.6, "fast_plate"))
            except Exception:
                pass

        return candidates


if __name__ == "__main__":
    print("PaddleOCR available:", _PADDLE_AVAILABLE)
    print("fast-plate-ocr available:", _FAST_PLATE_AVAILABLE)
    print("Run `pip install -r requirements.txt` if either is False.")
