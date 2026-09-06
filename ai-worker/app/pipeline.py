import os
import time
import cv2
import torch
import base64
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from paddleocr import PaddleOCR
from app.ocr_utils import create_plate_variants, extract_ocr_text

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
VEHICLE_CLASS_IDS = [2, 3, 5, 7]  # car, motorcycle, bus, truck

class TrafficVisionPipeline:
    def __init__(self):
        self.vehicle_model = None
        self.plate_model = None
        self.ocr = None
        self.loaded = False

    def load_models(self):
        print(f"Loading models on device: {DEVICE}")
        # 1. Vehicle Model
        self.vehicle_model = YOLO("yolo11n.pt")
        
        # 2. Plate Model
        print("Downloading/Loading plate model from Hugging Face...")
        plate_model_path = hf_hub_download(
            repo_id="Koushim/yolov8-license-plate-detection",
            filename="best.pt"
        )
        self.plate_model = YOLO(plate_model_path)
        
        # 3. PaddleOCR
        print("Loading PaddleOCR...")
        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            use_gpu=(DEVICE == "cuda")
        )
        
        self.loaded = True
        print("All models loaded successfully.")

    def run_ocr_variant(self, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        results = self.ocr.predict(img)
        text, conf = extract_ocr_text(results)
        return text, conf

    def process_image(self, frame):
        """Processes a single image and returns timings, counts, and base64 preview."""
        checkpoints = {}
        
        t0 = time.perf_counter()
        # Input loaded
        checkpoints["Input loaded"] = int((time.perf_counter() - t0) * 1000)
        
        # Vehicle detection
        t1 = time.perf_counter()
        vehicle_results = self.vehicle_model.predict(
            frame,
            classes=VEHICLE_CLASS_IDS,
            conf=0.25,
            device=DEVICE,
            verbose=False
        )[0]
        checkpoints["Vehicle detection"] = int((time.perf_counter() - t1) * 1000)
        vehicle_count = len(vehicle_results.boxes)
        
        # Plate detection
        t2 = time.perf_counter()
        plate_results = self.plate_model.predict(
            frame,
            conf=0.20,
            device=DEVICE,
            verbose=False
        )[0]
        checkpoints["Plate detection"] = int((time.perf_counter() - t2) * 1000)
        
        plate_boxes = plate_results.boxes
        plate_count = len(plate_boxes)
        
        # Preprocessing & OCR
        t3 = time.perf_counter()
        successful_ocr = 0
        ocr_results_list = []
        
        annotated_frame = vehicle_results.plot()
        annotated_frame = plate_results.plot(img=annotated_frame)
        
        preprocessing_time = 0
        ocr_time = 0
        
        if plate_count > 0:
            for plate_number in range(plate_count):
                x1, y1, x2, y2 = plate_boxes.xyxy[plate_number].cpu().numpy().astype(int)
                conf = float(plate_boxes.conf[plate_number].cpu().item())
                
                # Padding
                frame_h, frame_w = frame.shape[:2]
                pad_x = int((x2 - x1) * 0.08)
                pad_y = int((y2 - y1) * 0.15)
                
                x1 = max(0, x1 - pad_x)
                y1 = max(0, y1 - pad_y)
                x2 = min(frame_w, x2 + pad_x)
                y2 = min(frame_h, y2 + pad_y)
                
                plate_crop = frame[y1:y2, x1:x2]
                if plate_crop is None or plate_crop.size == 0:
                    continue
                
                # Preprocessing
                t_prep_start = time.perf_counter()
                variants = create_plate_variants(plate_crop)
                preprocessing_time += (time.perf_counter() - t_prep_start)
                
                # OCR
                t_ocr_start = time.perf_counter()
                best_text = "UNKNOWN"
                best_score = -1.0
                best_variant = "NONE"
                
                for variant_name, variant_image in variants.items():
                    text, confidence = self.run_ocr_variant(variant_image)
                    if text != "UNKNOWN" and confidence > best_score:
                        best_text = text
                        best_score = confidence
                        best_variant = variant_name
                
                ocr_time += (time.perf_counter() - t_ocr_start)
                
                ocr_results_list.append({
                    "text": best_text,
                    "confidence": best_score,
                    "variant": best_variant,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })
                
                if best_text != "UNKNOWN":
                    successful_ocr += 1
                    cv2.putText(
                        annotated_frame, 
                        f"{best_text} ({best_score:.2f})", 
                        (x1, max(20, y1 - 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0), 2
                    )

        checkpoints["Plate preprocessing"] = int(preprocessing_time * 1000)
        checkpoints["OCR"] = int(ocr_time * 1000)
        
        # Result generation
        t4 = time.perf_counter()
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        b64_img = base64.b64encode(buffer).decode('utf-8')
        checkpoints["Result generation"] = int((time.perf_counter() - t4) * 1000)
        
        checkpoints["Total"] = int((time.perf_counter() - t0) * 1000)
        
        return {
            "checkpoints": checkpoints,
            "counts": {
                "vehicles_detected": vehicle_count,
                "plates_detected": plate_count,
                "ocr_attempts": plate_count,
                "successful_ocr": successful_ocr
            },
            "ocr_results": ocr_results_list,
            "processed_image_base64": b64_img
        }
