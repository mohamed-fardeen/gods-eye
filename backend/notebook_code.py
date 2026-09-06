# IMPORTANT: Run this cell FIRST.
# The uploaded notebook installed paddlepaddle-gpu with CUDA 11 packages,
# while Colab's PyTorch used CUDA 12.8, which can break torch import.

!pip uninstall -y paddlepaddle-gpu nvidia-nccl-cu11 nvidia-cuda-runtime-cu11 nvidia-cudnn-cu11 nvidia-cublas-cu11 nvidia-cufft-cu11 nvidia-curand-cu11 nvidia-cusolver-cu11 nvidia-cusparse-cu11 nvidia-cuda-nvrtc-cu11 nvidia-cuda-cupti-cu11 nvidia-nvtx-cu11

# Install only the packages needed for this notebook.
!pip install -q -U ultralytics supervision huggingface_hub


---CELL---

import torch, subprocess, sys

print("Python:", sys.version)
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
else:
    raise RuntimeError("GPU is not available. In Colab select Runtime > Change runtime type > T4 GPU.")

!nvidia-smi


---CELL---

# Install the CPU Paddle runtime only for OCR.
# Vehicle + plate YOLO inference will still use the T4 through PyTorch.
!pip install -q -U paddleocr paddlepaddle


---CELL---

import os, re, cv2, torch, numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from google.colab import files
from ultralytics import YOLO
import supervision as sv
from huggingface_hub import hf_hub_download

DEVICE = 0 if torch.cuda.is_available() else "cpu"
print("Using device:", DEVICE)


---CELL---

# ============================================================
# CELL 1 — CHOOSE IMAGE FOLDER
# ============================================================

from google.colab import files
import os

# Colab does not provide a native folder picker,
# so we use the file picker to select/upload images
# from a folder.

print("Select the images you want to test.")

uploaded = files.upload()

# Get the folder from the uploaded files
uploaded_files = list(uploaded.keys())

if len(uploaded_files) == 0:
    print("No images selected.")
else:
    print(f"\nLoaded {len(uploaded_files)} image(s).")

---CELL---

# Pretrained vehicle model; automatically downloads if missing.
vehicle_model = YOLO("yolo11n.pt")
VEHICLE_CLASS_IDS = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Public pretrained license-plate detector from Hugging Face.
PLATE_MODEL_PATH = hf_hub_download(
    repo_id="Koushim/yolov8-license-plate-detection",
    filename="best.pt"
)
plate_model = YOLO(PLATE_MODEL_PATH)

print("Vehicle model ready")
print("Plate model:", PLATE_MODEL_PATH)


---CELL---

# ============================================================
# VEHICLE DETECTION TEST — ALL UPLOADED IMAGES
# ============================================================

import os
import cv2
import matplotlib.pyplot as plt


# Get all uploaded image files
image_paths = [
    path for path in uploaded.keys()
    if path.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
    )
]

print("=" * 70)
print(f"Found {len(image_paths)} image(s)")
print("=" * 70)


if len(image_paths) == 0:

    print("No images found.")

else:

    for i, image_path in enumerate(image_paths, start=1):

        print("\n" + "=" * 70)
        print(f"IMAGE {i}/{len(image_paths)}")
        print(f"File: {os.path.basename(image_path)}")
        print("=" * 70)


        # ----------------------------------------------------
        # Load image
        # ----------------------------------------------------

        frame = cv2.imread(image_path)

        if frame is None:
            print("Could not read image.")
            continue


        h, w = frame.shape[:2]

        print(f"Resolution: {w} × {h}")


        # ----------------------------------------------------
        # Vehicle detection
        # ----------------------------------------------------

        vehicle_results = vehicle_model.predict(
            frame,
            classes=VEHICLE_CLASS_IDS,
            conf=0.25,
            device=DEVICE,
            verbose=False
        )[0]


        # ----------------------------------------------------
        # Number of vehicles
        # ----------------------------------------------------

        vehicle_count = len(vehicle_results.boxes)

        print(f"Vehicles detected: {vehicle_count}")


        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        preview = vehicle_results.plot()


        plt.figure(figsize=(14, 8))

        plt.imshow(
            cv2.cvtColor(
                preview,
                cv2.COLOR_BGR2RGB
            )
        )

        plt.title(
            f"{os.path.basename(image_path)} | "
            f"Vehicles: {vehicle_count}"
        )

        plt.axis("off")
        plt.show()


print("\n" + "=" * 70)
print("VEHICLE DETECTION TEST COMPLETE")
print("=" * 70)

---CELL---

# ============================================================
# LICENSE PLATE DETECTION TEST — ALL UPLOADED IMAGES
# ============================================================

import os
import cv2
import matplotlib.pyplot as plt


# Get all uploaded image files
image_paths = [
    path for path in uploaded.keys()
    if path.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
    )
]


print("=" * 70)
print(f"Testing {len(image_paths)} image(s)")
print("=" * 70)


if len(image_paths) == 0:

    print("No images found.")

else:

    for i, image_path in enumerate(image_paths, start=1):

        print("\n" + "=" * 70)
        print(f"IMAGE {i}/{len(image_paths)}")
        print(f"File: {os.path.basename(image_path)}")
        print("=" * 70)


        # ----------------------------------------------------
        # Load image
        # ----------------------------------------------------

        frame = cv2.imread(image_path)

        if frame is None:
            print("Could not read image.")
            continue


        h, w = frame.shape[:2]

        print(f"Resolution: {w} × {h}")


        # ----------------------------------------------------
        # License plate detection
        # ----------------------------------------------------

        plate_results = plate_model.predict(
            frame,
            conf=0.20,
            device=DEVICE,
            verbose=False
        )[0]


        # ----------------------------------------------------
        # Number of plates
        # ----------------------------------------------------

        plate_count = len(
            plate_results.boxes
        )

        print(
            f"License plates detected: "
            f"{plate_count}"
        )


        # ----------------------------------------------------
        # Print confidence for every plate
        # ----------------------------------------------------

        if plate_count > 0:

            confidences = (
                plate_results.boxes.conf
                .cpu()
                .numpy()
            )

            for plate_number, confidence in enumerate(
                confidences,
                start=1
            ):

                print(
                    f"  Plate {plate_number}: "
                    f"{float(confidence):.2%}"
                )


        # ----------------------------------------------------
        # Display detection result
        # ----------------------------------------------------

        preview = plate_results.plot()


        plt.figure(figsize=(14, 8))

        plt.imshow(
            cv2.cvtColor(
                preview,
                cv2.COLOR_BGR2RGB
            )
        )

        plt.title(
            f"{os.path.basename(image_path)} | "
            f"Plates: {plate_count}"
        )

        plt.axis("off")
        plt.show()


print("\n" + "=" * 70)
print("LICENSE PLATE DETECTION TEST COMPLETE")
print("=" * 70)

---CELL---

# ============================================================
# OCR SETUP CELL (RUN ONCE)
# ============================================================

import cv2
import numpy as np
import re
from paddleocr import PaddleOCR

# Initialize PaddleOCR
ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

def clean_plate_text(text):
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())


def extract_ocr_text(results):
    texts, scores = [], []

    for result in results:
        data = {}

        if isinstance(result, dict):
            data = result
        elif hasattr(result, "json"):
            try:
                data = result.json() if callable(result.json) else result.json
            except:
                data = {}

        res = data.get("res", data) if isinstance(data, dict) else {}

        if isinstance(res, dict):
            rec_texts = res.get("rec_texts", [])
            rec_scores = res.get("rec_scores", [])

            for i, txt in enumerate(rec_texts):
                txt = str(txt).strip()
                if txt:
                    texts.append(txt)
                    scores.append(float(rec_scores[i]) if i < len(rec_scores) else 0)

    text = clean_plate_text("".join(texts))
    confidence = np.mean(scores) if scores else 0

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


def run_ocr_variant(img):
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    text, conf = extract_ocr_text(ocr.predict(img))
    return text, conf


def read_plate(crop):
    variants = create_plate_variants(crop)

    best_text = "UNKNOWN"
    best_conf = -1
    best_variant = None

    for name, img in variants.items():
        text, conf = run_ocr_variant(img)

        if text != "UNKNOWN" and conf > best_conf:
            best_text = text
            best_conf = conf
            best_variant = name

    return best_text, best_variant, best_conf

print("✅ PaddleOCR ready with 5 preprocessing variants.")

---CELL---

# ============================================================
# OCR TEST — ALL UPLOADED IMAGES + ALL DETECTED PLATES
# ============================================================

import os
import cv2
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Get ALL uploaded images
# ------------------------------------------------------------

image_paths = [
    path for path in uploaded.keys()
    if path.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
    )
]


print("=" * 70)
print(f"Found {len(image_paths)} uploaded image(s)")
print("=" * 70)


total_plates = 0
successful_ocr = 0


# ============================================================
# PROCESS EVERY IMAGE
# ============================================================

for image_number, image_path in enumerate(
    image_paths,
    start=1
):

    print("\n")
    print("=" * 70)
    print(
        f"IMAGE {image_number}/{len(image_paths)}"
    )
    print(
        f"File: {os.path.basename(image_path)}"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # Load ORIGINAL image
    # --------------------------------------------------------

    frame = cv2.imread(
        image_path
    )


    if frame is None:

        print(
            "Could not read image."
        )

        continue


    frame_h, frame_w = frame.shape[:2]


    print(
        f"Original resolution: "
        f"{frame_w} × {frame_h}"
    )


    # --------------------------------------------------------
    # Detect plates
    # --------------------------------------------------------

    plate_results = plate_model.predict(
        frame,
        conf=0.20,
        device=DEVICE,
        verbose=False
    )[0]


    boxes = plate_results.boxes


    # --------------------------------------------------------
    # No plates detected
    # --------------------------------------------------------

    if (
        boxes is None
        or len(boxes) == 0
    ):

        print(
            "No license plate detected."
        )

        continue


    print(
        f"Detected {len(boxes)} plate(s)"
    )


    # ========================================================
    # PROCESS EVERY DETECTED PLATE
    # ========================================================

    for plate_number in range(
        len(boxes)
    ):

        print("\n")
        print("-" * 60)
        print(
            f"PLATE {plate_number + 1}/{len(boxes)}"
        )
        print("-" * 60)


        # ----------------------------------------------------
        # Get bounding box
        # ----------------------------------------------------

        x1, y1, x2, y2 = (
            boxes.xyxy[plate_number]
            .cpu()
            .numpy()
            .astype(int)
        )


        # ----------------------------------------------------
        # Padding
        # ----------------------------------------------------

        pad_x = int(
            (x2 - x1) * 0.08
        )

        pad_y = int(
            (y2 - y1) * 0.15
        )


        x1 = max(
            0,
            x1 - pad_x
        )

        y1 = max(
            0,
            y1 - pad_y
        )

        x2 = min(
            frame_w,
            x2 + pad_x
        )

        y2 = min(
            frame_h,
            y2 + pad_y
        )


        # ----------------------------------------------------
        # IMPORTANT:
        # Crop from ORIGINAL frame
        # ----------------------------------------------------

        plate_crop = frame[
            y1:y2,
            x1:x2
        ]


        if (
            plate_crop is None
            or plate_crop.size == 0
        ):

            print(
                "Invalid plate crop."
            )

            continue


        # ----------------------------------------------------
        # Plate resolution
        # ----------------------------------------------------

        plate_h, plate_w = (
            plate_crop.shape[:2]
        )


        print(
            f"Plate resolution: "
            f"{plate_w} × {plate_h}"
        )


        # ----------------------------------------------------
        # Detection confidence
        # ----------------------------------------------------

        detection_confidence = float(
            boxes.conf[plate_number]
            .cpu()
            .item()
        )


        print(
            f"Detection confidence: "
            f"{detection_confidence:.2%}"
        )


        total_plates += 1


        # ====================================================
        # CREATE OCR VARIANTS
        # ====================================================

        variants = create_plate_variants(
            plate_crop
        )


        print(
            f"\nGenerated {len(variants)} OCR variants"
        )


        # ====================================================
        # DISPLAY VARIANTS
        # ====================================================

        for variant_name, variant_image in variants.items():

            plt.figure(
                figsize=(12, 3)
            )

            plt.imshow(
                cv2.cvtColor(
                    variant_image,
                    cv2.COLOR_BGR2RGB
                )
            )

            plt.title(
                f"{os.path.basename(image_path)} | "
                f"Plate {plate_number + 1} | "
                f"{variant_name}"
            )

            plt.axis("off")
            plt.show()


        # ====================================================
        # OCR EVERY VARIANT
        # ====================================================

        print("\nOCR RESULTS:")


        best_text = "UNKNOWN"
        best_score = -1.0
        best_variant = "NONE"


        for variant_name, variant_image in variants.items():

            text, confidence = run_ocr_variant(
                variant_image
            )


            print(
                f"{variant_name:25s} "
                f"→ {text:15s} "
                f"| confidence: "
                f"{confidence:.2%}"
            )


            if (
                text != "UNKNOWN"
                and confidence > best_score
            ):

                best_text = text
                best_score = confidence
                best_variant = variant_name


        # ----------------------------------------------------
        # Final OCR result
        # ----------------------------------------------------

        print(
            f"\nFINAL OCR: {best_text}"
        )

        print(
            f"BEST VARIANT: {best_variant}"
        )


        if best_text != "UNKNOWN":

            successful_ocr += 1


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("OCR TEST COMPLETE")
print("=" * 70)

print(
    f"Total plates tested: "
    f"{total_plates}"
)

print(
    f"Successful OCR results: "
    f"{successful_ocr}"
)

if total_plates > 0:

    print(
        f"OCR success rate: "
        f"{successful_ocr / total_plates:.2%}"
    )

print("=" * 70)

---CELL---

OUTPUT_PATH = "/content/output_traffic_analysis.mp4"

tracker = sv.ByteTrack(track_activation_threshold=0.25, lost_track_buffer=30)

# Change these percentages if needed after seeing the output.
COUNT_LINE_Y_RATIO = 0.55
trajectory_history = defaultdict(lambda: deque(maxlen=30))
last_side = {}
counted_ids = set()
direction_counts = defaultdict(int)
plate_cache = {}

def movement_direction(points):
    if len(points) < 5:
        return "unknown"
    x0, y0 = points[0]
    x1, y1 = points[-1]
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) > abs(dy):
        return "left_to_right" if dx > 0 else "right_to_left"
    return "top_to_bottom" if dy > 0 else "bottom_to_top"

def associate_plate(vehicle_box, plate_boxes):
    vx1, vy1, vx2, vy2 = vehicle_box
    best = None
    best_conf = -1
    for px1, py1, px2, py2, conf in plate_boxes:
        cx, cy = (px1 + px2) / 2, (py1 + py2) / 2
        if vx1 <= cx <= vx2 and vy1 <= cy <= vy2 and conf > best_conf:
            best = (int(px1), int(py1), int(px2), int(py2))
            best_conf = conf
    return best

def process_frame(frame, frame_index):
    global last_side

    # 1) Vehicle detection
    vr = vehicle_model.predict(
        frame, classes=VEHICLE_CLASS_IDS, conf=0.25,
        device=DEVICE, verbose=False
    )[0]
    detections = sv.Detections.from_ultralytics(vr)
    detections = tracker.update_with_detections(detections)

    # 2) Plate detection every 5 frames to keep the T4 pipeline fast
    plate_boxes = []
    if frame_index % 5 == 0:
        pr = plate_model.predict(frame, conf=0.20, device=DEVICE, verbose=False)[0]
        if len(pr.boxes):
            xyxy = pr.boxes.xyxy.cpu().numpy()
            confs = pr.boxes.conf.cpu().numpy()
            plate_boxes = [
                (*box.astype(float), float(conf))
                for box, conf in zip(xyxy, confs)
            ]

    annotated = frame.copy()
    H, W = frame.shape[:2]
    line_y = int(H * COUNT_LINE_Y_RATIO)

    # Counting and density
    current_vehicle_count = len(detections)
    if current_vehicle_count < 5:
        density = "LOW"
    elif current_vehicle_count < 15:
        density = "MEDIUM"
    else:
        density = "HIGH"

    # Draw counting line
    cv2.line(annotated, (0, line_y), (W, line_y), (255, 255, 255), 2)

    if len(detections) and detections.tracker_id is not None:
        for box, cls_id, conf, tid in zip(
            detections.xyxy,
            detections.class_id,
            detections.confidence,
            detections.tracker_id
        ):
            x1, y1, x2, y2 = box.astype(int)
            tid = int(tid)
            cls_name = vehicle_model.names[int(cls_id)]

            # Trajectory
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            trajectory_history[tid].append((cx, cy))
            direction = movement_direction(trajectory_history[tid])

            # Line crossing: count each ID once
            side = cy >= line_y
            if tid in last_side and last_side[tid] != side and tid not in counted_ids:
                counted_ids.add(tid)
                direction_counts[cls_name] += 1
            last_side[tid] = side

            # Plate + OCR
            if frame_index % 5 == 0 and tid not in plate_cache:
                pbox = associate_plate((x1, y1, x2, y2), plate_boxes)
                if pbox:
                    px1, py1, px2, py2 = pbox
                    crop = frame[py1:py2, px1:px2]
                    plate_cache[tid] = read_plate(crop)
                    cv2.rectangle(annotated, (px1, py1), (px2, py2), (255, 255, 255), 1)

            plate_text = plate_cache.get(tid, "...")
            label = f"ID {tid} | {cls_name} | {plate_text} | {direction}"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(
                annotated, label, (x1, max(25, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1,
                cv2.LINE_AA
            )

            pts = list(trajectory_history[tid])
            for a, b in zip(pts[:-1], pts[1:]):
                cv2.line(annotated, a, b, (200, 200, 200), 2)

    cv2.putText(annotated, f"Vehicles now: {current_vehicle_count}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(annotated, f"Traffic density: {density}", (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(annotated, f"Unique crossings: {len(counted_ids)}", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return annotated


---CELL---



---CELL---

if is_image:
    frame = cv2.imread(INPUT_PATH)
    output = process_frame(frame, 0)
    IMAGE_OUTPUT = "/content/output_traffic_analysis.jpg"
    cv2.imwrite(IMAGE_OUTPUT, output)

    plt.figure(figsize=(16, 9))
    plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()
    print("Saved:", IMAGE_OUTPUT)

else:
    cap = cv2.VideoCapture(INPUT_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    writer = cv2.VideoWriter(
        OUTPUT_PATH,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        output = process_frame(frame, frame_index)
        writer.write(output)
        frame_index += 1

        if frame_index % 50 == 0:
            print(f"Processed {frame_index}/{total} frames")

    cap.release()
    writer.release()
    print("Saved:", OUTPUT_PATH)
    print("Crossings by class:", dict(direction_counts))


---CELL---

from IPython.display import HTML, display
from base64 import b64encode

if is_image:
    files.download(IMAGE_OUTPUT)
else:
    # Convert to browser-friendly H.264 MP4.
    !ffmpeg -y -loglevel error -i "$OUTPUT_PATH" -vcodec libx264 -pix_fmt yuv420p /content/output_browser.mp4

    mp4 = open("/content/output_browser.mp4", "rb").read()
    data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
    display(HTML(f'<video width="900" controls><source src="{data_url}" type="video/mp4"></video>'))

    files.download("/content/output_browser.mp4")
