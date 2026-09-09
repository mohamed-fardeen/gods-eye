"""
Fine-tune YOLOv8 for Indian license-plate detection on an RTX 5050 (8GB).

Assumes data/processed/plate_detection/data.yaml already exists in YOLO
format (see scripts/prepare_dataset.py). Do NOT train from scratch —
starts from yolov8n.pt (or yolov8s.pt if VRAM allows, see notes below).

RTX 5050 8GB guidance:
  - imgsz=640, batch=16, yolov8n -> comfortably fits with AMP, ~fast epochs.
  - If you see CUDA OOM: drop batch to 8, or imgsz to 512, before dropping
    model size (yolov8n is already the smallest sensible option).
  - yolov8s.pt gives a real accuracy bump if batch=8 still fits after
    switching — worth trying once yolov8n baseline is measured.
  - AMP (mixed precision) is enabled by default in Ultralytics; do not
    disable it, it roughly halves VRAM use with negligible accuracy cost.
"""

import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/processed/plate_detection/data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="yolov8n.pt (default, fastest) or yolov8s.pt (more accurate, needs more VRAM)")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="0")
    parser.add_argument("--patience", type=int, default=15, help="early stop if val mAP plateaus")
    args = parser.parse_args()

    model = YOLO(args.model)  # pretrained COCO weights, NOT random init
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        amp=True,
        patience=args.patience,
        project="models",
        name="plate_detector",
        exist_ok=True,
        # Light augmentation only — heavy augmentation on an already-small
        # plate object can push it below detectable size.
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        fliplr=0.0,  # NEVER flip: plate text becomes unreadable / mirrored
    )
    print("Training complete. Best checkpoint at models/plate_detector/weights/best.pt")
    print("Copy it to models/plate_detector_best.pt to be picked up by app/plate/plate_detector.py:")
    print("  cp models/plate_detector/weights/best.pt models/plate_detector_best.pt")


if __name__ == "__main__":
    main()
