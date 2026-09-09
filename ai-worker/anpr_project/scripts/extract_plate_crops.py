from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def extract_crops(
    model_path: str,
    image_dir: str,
    output_dir: str,
    conf: float = 0.25,
    imgsz: int = 640,
) -> None:
    model = YOLO(model_path)

    input_dir = Path(image_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    images = [
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not images:
        raise FileNotFoundError(f"No images found in: {input_dir}")

    total_crops = 0

    for index, image_path in enumerate(images, start=1):
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"[WARN] Could not read: {image_path}")
            continue

        results = model.predict(
            source=image,
            conf=conf,
            imgsz=imgsz,
            device=0,
            verbose=False,
        )

        result = results[0]

        if result.boxes is None or len(result.boxes) == 0:
            continue

        # Save every detected plate.
        for det_idx, box in enumerate(result.boxes.xyxy.cpu().numpy()):
            x1, y1, x2, y2 = box.astype(int)

            h, w = image.shape[:2]

            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(x1 + 1, min(x2, w))
            y2 = max(y1 + 1, min(y2, h))

            crop = image[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            stem = image_path.stem
            output_file = output_path / f"{stem}_plate_{det_idx}.jpg"

            cv2.imwrite(str(output_file), crop)
            total_crops += 1

        if index % 25 == 0 or index == len(images):
            print(
                f"Processed {index}/{len(images)} images | "
                f"plate crops: {total_crops}"
            )

    print("\n========================================")
    print("PLATE CROP EXTRACTION COMPLETE")
    print("========================================")
    print(f"Images processed: {len(images)}")
    print(f"Plate crops saved: {total_crops}")
    print(f"Output directory: {output_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        default="models/plate_detector_best.pt",
    )

    parser.add_argument(
        "--images",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
    )

    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
    )

    args = parser.parse_args()

    extract_crops(
        model_path=args.model,
        image_dir=args.images,
        output_dir=args.output,
        conf=args.conf,
        imgsz=args.imgsz,
    )


if __name__ == "__main__":
    main()
