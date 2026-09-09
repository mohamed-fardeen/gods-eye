import os
import time
import cv2
import torch
import base64
import sys
from ultralytics import YOLO
import numpy as np

# Add anpr_project to path so we can import its modules seamlessly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "anpr_project"))

import subprocess
from app.anpr.temporal_fusion import ObservationRecord, fuse_observations
from app.realtime.ocr_worker import OCRClient

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_GPU = torch.cuda.is_available()

VEHICLE_CLASS_IDS = [2, 3, 5, 7]  # car, motorcycle, bus, truck

class TrafficVisionPipeline:
    def __init__(self):
        self.vehicle_model = None
        self.plate_model = None
        self.ocr = None
        self.loaded = False
        
        self.frame_count = 0
        self.track_buffers = {}
        
        # Keep track of vehicles that have an "CONFIRMED" status so we don't keep OCRing them
        self.locked_plates = {}

    def load_models(self):
        print(f"Loading models on device: {DEVICE}")
        
        base_path = os.path.join(os.path.dirname(__file__), "..", "anpr_project")
        
        # 1. Vehicle Model (from anpr_project)
        vehicle_model_path = os.path.join(base_path, "yolov8n.pt")
        self.vehicle_model = YOLO(vehicle_model_path)
        
        # 2. Plate Model (from anpr_project)
        plate_model_path = os.path.join(base_path, "models", "plate_detector", "weights", "best.pt")
        self.plate_model = YOLO(plate_model_path)
        
        # 3. OCR (pp-ocrv6 from anpr_project via OCRClient)
        print("Starting PP-OCRv6 Server in a separate process...")
        ocr_server_script = os.path.join(base_path, "app", "realtime", "ocr_server.py")
        self.ocr_server_process = subprocess.Popen([sys.executable, ocr_server_script])
        
        print("Connecting OCRClient...")
        self.ocr = OCRClient()
        
        self.loaded = True
        print(f"All models loaded successfully from anpr_project on {DEVICE}.")

    def cleanup(self):
        if hasattr(self, 'ocr_server_process') and self.ocr_server_process:
            print("Terminating OCR server process...")
            self.ocr_server_process.terminate()
            try:
                self.ocr_server_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.ocr_server_process.kill()
        if hasattr(self, 'ocr') and self.ocr:
            try:
                self.ocr.close()
            except:
                pass

    def process_image(self, frame):
        """Processes a single image and integrates ANPR logic."""
        self.frame_count += 1
        t0 = time.perf_counter()
        
        # 1. Vehicle detection & Tracking
        vehicle_results = self.vehicle_model.track(
            frame,
            classes=VEHICLE_CLASS_IDS,
            conf=0.25,
            persist=True,
            device=DEVICE,
            verbose=False,
            tracker="bytetrack.yaml",
            imgsz=512
        )[0]
        
        annotated_frame = frame.copy()
        
        v_boxes = vehicle_results.boxes
        if v_boxes is None or len(v_boxes) == 0:
            _, b_buffer = cv2.imencode('.jpg', annotated_frame)
            return {
                "checkpoints": {"Total": int((time.perf_counter() - t0) * 1000)},
                "counts": {"vehicles_detected": 0},
                "ocr_results": [],
                "processed_image_base64": base64.b64encode(b_buffer).decode('utf-8')
            }
            
        v_xyxy = v_boxes.xyxy.cpu().numpy().astype(int)
        v_conf = v_boxes.conf.cpu().numpy()
        v_cls = v_boxes.cls.cpu().numpy().astype(int)
        v_ids = v_boxes.id.cpu().numpy().astype(int) if v_boxes.id is not None else [None] * len(v_cls)
        
        plate_inputs = []
        plate_meta = []
        height, width = frame.shape[:2]
        
        # 1a. Extract vehicle crops for plate detection
        for i, (box, c, cl, tid) in enumerate(zip(v_xyxy, v_conf, v_cls, v_ids)):
            if tid is None: continue
            
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            
            if w > 60 and h > 40:
                px1 = max(0, x1 - int(w*0.05))
                py1 = max(0, y1 - int(h*0.05))
                px2 = min(width, x2 + int(w*0.05))
                py2 = min(height, y2 + int(h*0.05))
                
                v_crop = frame[py1:py2, px1:px2]
                if v_crop.size > 0:
                    plate_inputs.append(v_crop)
                    plate_meta.append({
                        'track_id': tid, 'vx1': px1, 'vy1': py1, 'vclass': cl, 'vconf': c, 'vbox': (x1, y1, x2, y2)
                    })

        ocr_requests = []
        ocr_meta_map = {}
        
        # 2. Plate Detection on Crops
        if plate_inputs:
            plate_results = self.plate_model.predict(
                plate_inputs,
                imgsz=416,
                conf=0.20,
                device=DEVICE,
                verbose=False
            )
            
            for r_idx, pres in enumerate(plate_results):
                pboxes = pres.boxes
                if pboxes is None or len(pboxes) == 0: continue
                
                best_idx = int(pboxes.conf.argmax().item())
                pb = pboxes.xyxy[best_idx].cpu().numpy()
                pc = pboxes.conf[best_idx].cpu().item()
                
                px1, py1, px2, py2 = map(int, pb)
                meta = plate_meta[r_idx]
                tid = meta['track_id']
                
                # Skip OCR if we have already confidently LOCKED the plate
                if tid in self.locked_plates:
                    continue
                
                gx1 = meta['vx1'] + px1
                gy1 = meta['vy1'] + py1
                gx2 = meta['vx1'] + px2
                gy2 = meta['vy1'] + py2
                
                p_crop = frame[gy1:gy2, gx1:gx2]
                if p_crop.size > 0:
                    ocr_item = {
                        "track_id": tid,
                        "frame_id": self.frame_count,
                        "crop": p_crop
                    }
                    ocr_requests.append(ocr_item)
                    ocr_meta_map[tid] = {
                        'pconf': pc, 'pbox': (gx1, gy1, gx2, gy2),
                        'vclass': meta['vclass'], 'vconf': meta['vconf']
                    }
        
        # 3. Batch OCR Request
        if ocr_requests and self.ocr:
            req_id = self.ocr.submit(ocr_requests)
            if req_id != -1:
                try:
                    resp = self.ocr.receive(timeout=3.0)
                    if resp and "results" in resp:
                        for res in resp["results"]:
                            tid = res["track_id"]
                            text = res["text"]
                            score = res["confidence"]
                            if not text: continue
                            
                            meta = ocr_meta_map.get(tid)
                            if not meta: continue
                            
                            if tid not in self.track_buffers:
                                self.track_buffers[tid] = []
                            
                            # Calculate a simple dummy quality score based on bounding box size
                            w_p = meta['pbox'][2] - meta['pbox'][0]
                            h_p = meta['pbox'][3] - meta['pbox'][1]
                            quality = min(1.0, (w_p * h_p) / (150 * 50))
                            
                            obs = ObservationRecord(
                                frame_id=self.frame_count,
                                track_id=tid,
                                raw_text=text,
                                normalized_text=text.upper().replace(" ", "").replace("-", ""),
                                ocr_confidence=score,
                                detector_confidence=meta['pconf'],
                                quality_score=quality,
                                timestamp=t0
                            )
                            self.track_buffers[tid].append(obs)
                            if len(self.track_buffers[tid]) > 12:
                                self.track_buffers[tid].pop(0)
                except Exception as e:
                    print(f"OCR batch receive error: {e}")

        # 4. Fuse and Annotate
        ocr_results_list = []
        for meta in plate_meta:
            tid = meta['track_id']
            vx1, vy1, vx2, vy2 = meta['vbox']
            
            # Draw vehicle box
            cv2.rectangle(annotated_frame, (vx1, vy1), (vx2, vy2), (255, 255, 0), 2)
            
            fused_text = "UNREADABLE"
            fused_conf = 0.0
            
            if tid in self.locked_plates:
                fused_text, fused_conf = self.locked_plates[tid]
                decision = "LOCKED"
                color = (0, 255, 0)
                
                # Draw plate box if detected this frame
                p_meta = ocr_meta_map.get(tid)
                if p_meta:
                    gx1, gy1, gx2, gy2 = p_meta['pbox']
                    cv2.rectangle(annotated_frame, (gx1, gy1), (gx2, gy2), (255, 0, 0), 2)
            else:
                decision = "UNREADABLE"
                color = (0, 255, 255)
                
                # Draw plate box if detected this frame
                p_meta = ocr_meta_map.get(tid)
                if p_meta:
                    gx1, gy1, gx2, gy2 = p_meta['pbox']
                    cv2.rectangle(annotated_frame, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)
                
                if tid in self.track_buffers and self.track_buffers[tid]:
                    fused_res = fuse_observations(self.track_buffers[tid], track_id=tid)
                    decision = fused_res.decision
                    if decision in ["CONFIRMED", "PROBABLE"] and fused_res.fused_text:
                        fused_text = fused_res.fused_text
                        fused_conf = fused_res.confidence
                        
                        # Relax validation to show green box for test plates
                        if decision == "CONFIRMED" or (decision == "PROBABLE" and fused_conf >= 0.50 and len(self.track_buffers[tid]) >= 2):
                            self.locked_plates[tid] = (fused_text, fused_conf)
                            decision = "LOCKED"
                            color = (0, 255, 0)
                        else:
                            color = (0, 165, 255)
            
            if fused_text != "UNREADABLE":
                ocr_results_list.append({
                    "text": fused_text,
                    "confidence": fused_conf,
                    "bbox": [int(vx1), int(vy1), int(vx2), int(vy2)]
                })
                
            display_text = f"ID:{tid} | {fused_text if fused_text != 'UNREADABLE' else 'No Plate'} [{decision}]"
            cv2.putText(annotated_frame, display_text, (vx1, max(20, vy1 - 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        _, b_buffer = cv2.imencode('.jpg', annotated_frame)
        b64_img = base64.b64encode(b_buffer).decode('utf-8')
        
        return {
            "checkpoints": {"Total": int((time.perf_counter() - t0) * 1000)},
            "counts": {"vehicles_detected": len(v_boxes)},
            "ocr_results": ocr_results_list,
            "processed_image_base64": b64_img
        }
