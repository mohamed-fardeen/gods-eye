import csv
from pathlib import Path

src = Path("outputs/ppocrv6_finetuned_predictions.txt")
dst = Path("outputs/ppocrv6_finetuned_predictions.csv")

rows = []

with src.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue

        # PaddleOCR native format:
        # full_image_path <spaces> predicted_text <spaces> confidence
        parts = line.rsplit(None, 2)
        if len(parts) != 3:
            continue

        image_path, text, confidence = parts
        filename = Path(image_path).name

        # Convert e.g. XXX_plate_0.jpg -> XXX.jpg
        if "_plate_" in filename:
            filename = filename.rsplit("_plate_", 1)[0] + ".jpg"

        rows.append({
            "image": filename,
            "prediction": text.strip(),
            "ocr_confidence": float(confidence),
        })

with dst.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["image", "prediction", "ocr_confidence"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} predictions to {dst}")
