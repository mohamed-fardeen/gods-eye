import cv2
import numpy as np
import re

def clean_plate_text(text):
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())

def extract_ocr_text(results):
    texts, scores = [], []
    
    # Handle None or empty results
    if not results or not results[0]:
        return "UNKNOWN", 0.0

    # PaddleOCR usually returns a list of lists.
    # results[0] contains the bounding boxes and text predictions for one image
    for res in results[0]:
        # res format: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ('text', confidence)]
        if len(res) == 2 and isinstance(res[1], (tuple, list)):
            txt, conf = res[1]
            txt = str(txt).strip()
            if txt:
                texts.append(txt)
                scores.append(float(conf))

    text = clean_plate_text("".join(texts))
    confidence = np.mean(scores) if scores else 0.0

    return text if text else "UNKNOWN", confidence


def create_plate_variants(crop):
    h, w = crop.shape[:2]

    scale = max(1.0, 160 / max(h, 1))

    crop = cv2.resize(
        crop,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_LANCZOS4
    )

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    clahe_gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(crop, (0, 0), 1)
    sharp = cv2.addWeighted(crop, 1.35, blur, -0.35, 0)

    clahe_color = cv2.cvtColor(clahe_gray, cv2.COLOR_GRAY2BGR)
    blur2 = cv2.GaussianBlur(clahe_color, (0, 0), 1)
    clahe_sharp = cv2.addWeighted(clahe_color, 1.25, blur2, -0.25, 0)

    return {
        "Original": crop,
        "Gray": cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
        "CLAHE": clahe_color,
        "Sharpened": sharp,
        "CLAHE+Sharp": clahe_sharp,
    }
