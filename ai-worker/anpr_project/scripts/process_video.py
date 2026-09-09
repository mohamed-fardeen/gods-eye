import sys
import os
import time
import csv
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Import fusion, validation, and OCRClient from existing components
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
from app.anpr.temporal_fusion import ObservationRecord, fuse_observations
from app.validation.plate_validator import validate_plate
from app.realtime.ocr_worker import OCRClient

def main():
    INPUT_VIDEO = PROJECT_ROOT / "input_video.mp4"
    if not INPUT_VIDEO.exists():
        # Maybe it's in the Downloads folder root
        INPUT_VIDEO = Path(r"C:\Users\imdad\Downloads\input_video.mp4")
        if not INPUT_VIDEO.exists():
            # WSL path
            INPUT_VIDEO = Path("/mnt/c/Users/imdad/Downloads/input_video.mp4")
            if not INPUT_VIDEO.exists():
                print(f"Error: input_video.mp4 not found.")
                return

    OUTPUT_DIR = PROJECT_ROOT / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_VIDEO = OUTPUT_DIR / f"{INPUT_VIDEO.stem}_anpr_annotated.mp4"
    OUTPUT_CSV = OUTPUT_DIR / f"{INPUT_VIDEO.stem}_anpr_results.csv"

    print("Loading models...")
    use_gpu = torch.cuda.is_available()
    device = 0 if use_gpu else "cpu"
    
    # Vehicle Model
    vehicle_model = YOLO(str(PROJECT_ROOT / "yolov8n.pt"))
    if use_gpu: vehicle_model.model.half()
    
    # Plate Model
    plate_model = YOLO(str(PROJECT_ROOT / "models/plate_detector/weights/best.pt"))
    if use_gpu: plate_model.model.half()
    
    # Connect to existing OCR Server
    print("Connecting to OCR Server...")
    ocr_client = OCRClient()

    cap = cv2.VideoCapture(str(INPUT_VIDEO))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(OUTPUT_VIDEO), fourcc, fps, (width, height))
    
    csv_file = open(OUTPUT_CSV, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "frame_id", "timestamp", "track_id", "vehicle_class", "vehicle_confidence",
        "plate_bbox", "plate_text", "ocr_confidence", "fused_plate", "fused_confidence"
    ])

    track_buffers = {}
    VEHICLE_CLASSES = [2, 3, 5, 7] # car, motorcycle, bus, truck

    frame_id = 0
    t_start = time.perf_counter()
    
    total_vehicles = 0
    total_plates = 0
    total_ocr = 0
    total_recognized = set()
    
    print(f"Processing {total_frames} frames...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_id += 1
        timestamp = time.perf_counter()

        # 1. Vehicle Tracking
        vehicle_results = vehicle_model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=VEHICLE_CLASSES,
            conf=0.25,
            imgsz=512,
            device=device,
            verbose=False,
        )
        
        result = vehicle_results[0]
        boxes = result.boxes
        
        if boxes is None or len(boxes) == 0:
            out.write(frame)
            continue
            
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)
        ids = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else [None] * len(cls)
        
        plate_inputs = []
        plate_meta = []
        
        for i, (box, c, cl, tid) in enumerate(zip(xyxy, conf, cls, ids)):
            if tid is None: continue
            
            x1, y1, x2, y2 = map(int, box)
            
            # Crop vehicle for plate detection
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
                        'track_id': tid, 'vx1': px1, 'vy1': py1, 'vclass': cl, 'vconf': c, 'vbox': (x1,y1,x2,y2)
                    })
                    total_vehicles += 1

        ocr_requests = []
        ocr_meta_map = {}
        
        # 2. Plate Detection
        if plate_inputs:
            plate_results = plate_model.predict(
                plate_inputs,
                imgsz=416,
                conf=0.20,
                device=device,
                verbose=False,
            )
            
            for r_idx, pres in enumerate(plate_results):
                pboxes = pres.boxes
                if pboxes is None or len(pboxes) == 0: continue
                
                best_idx = int(pboxes.conf.argmax().item())
                pb = pboxes.xyxy[best_idx].cpu().numpy()
                pc = pboxes.conf[best_idx].cpu().item()
                
                px1, py1, px2, py2 = map(int, pb)
                meta = plate_meta[r_idx]
                
                gx1 = meta['vx1'] + px1
                gy1 = meta['vy1'] + py1
                gx2 = meta['vx1'] + px2
                gy2 = meta['vy1'] + py2
                
                p_crop = frame[gy1:gy2, gx1:gx2]
                if p_crop.size > 0:
                    total_plates += 1
                    ocr_item = {
                        "track_id": meta['track_id'],
                        "frame_id": frame_id,
                        "crop": p_crop
                    }
                    ocr_requests.append(ocr_item)
                    ocr_meta_map[meta['track_id']] = {
                        'pconf': pc, 'pbox': (gx1, gy1, gx2, gy2),
                        'vclass': meta['vclass'], 'vconf': meta['vconf']
                    }

        # 3. OCR via Server
        if ocr_requests:
            req_id = ocr_client.submit(ocr_requests)
            if req_id != -1:
                resp = ocr_client.receive(timeout=5.0)
                if resp and "results" in resp:
                    for res in resp["results"]:
                        tid = res["track_id"]
                        text = res["text"]
                        score = res["confidence"]
                        if not text: continue
                        
                        meta = ocr_meta_map.get(tid)
                        if not meta: continue
                        
                        if tid not in track_buffers:
                            track_buffers[tid] = []
                            
                        # Dummy quality score based on plate crop size
                        w = meta['pbox'][2] - meta['pbox'][0]
                        h = meta['pbox'][3] - meta['pbox'][1]
                        quality = min(1.0, (w * h) / (150 * 50))
                        
                        obs = ObservationRecord(
                            frame_id=frame_id,
                            track_id=tid,
                            raw_text=text,
                            normalized_text=text.upper().replace(" ", "").replace("-", ""),
                            ocr_confidence=score,
                            detector_confidence=meta['pconf'],
                            quality_score=quality,
                            timestamp=timestamp
                        )
                        track_buffers[tid].append(obs)
                        if len(track_buffers[tid]) > 12:
                            track_buffers[tid].pop(0)
                            
                        total_ocr += 1

        # 4. Draw ALL vehicles in frame
        for meta in plate_meta:
            tid = meta['track_id']
            vbox = meta['vbox']
            vx1, vy1, vx2, vy2 = vbox
            
            # Draw vehicle box
            cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), (255, 255, 0), 2)
            
            fused_text = "UNREADABLE"
            fused_conf = 0.0
            ocr_conf = 0.0
            
            # Draw plate box if detected this frame
            p_meta = ocr_meta_map.get(tid)
            if p_meta:
                gx1, gy1, gx2, gy2 = p_meta['pbox']
                cv2.rectangle(frame, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)
            
            if tid in track_buffers and track_buffers[tid]:
                latest_obs = track_buffers[tid][-1]
                ocr_conf = latest_obs.ocr_confidence
                
                fused_res = fuse_observations(track_buffers[tid], track_id=tid)
                if fused_res.decision in ["CONFIRMED", "PROBABLE"] and fused_res.fused_text:
                    fused_text = fused_res.fused_text
                    fused_conf = fused_res.confidence
                    total_recognized.add(tid)
                    
                    pbox_str = str(p_meta['pbox']) if p_meta else ""
                    csv_writer.writerow([
                        frame_id, f"{timestamp:.3f}", tid, meta['vclass'], f"{meta['vconf']:.3f}",
                        pbox_str, latest_obs.normalized_text, f"{ocr_conf:.3f}", fused_text, f"{fused_conf:.3f}"
                    ])
            
            label_id = f"Vehicle ID: {tid}"
            label_ocr = f"OCR: {ocr_conf:.2f}"
            
            if fused_text == "UNREADABLE":
                label_plate = "Plate: UNREADABLE"
                label_final = "Final: --"
            else:
                label_plate = f"Plate: {fused_text}"
                label_final = f"Final: {fused_conf:.2f}"
                
            y_offset = max(20, vy1 - 50)
            cv2.putText(frame, label_id, (vx1, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, label_plate, (vx1, y_offset + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            cv2.putText(frame, label_ocr, (vx1, y_offset + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, label_final, (vx1, y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        out.write(frame)
        
        if frame_id % 30 == 0:
            elapsed = time.perf_counter() - t_start
            fps_current = frame_id / elapsed
            print(f"Processed {frame_id}/{total_frames} frames ({fps_current:.1f} fps)")

    out.release()
    cap.release()
    csv_file.close()
    
    elapsed = time.perf_counter() - t_start
    avg_fps = frame_id / elapsed if elapsed > 0 else 0
    
    print("\n" + "="*50)
    print("PROCESSING COMPLETE")
    print("="*50)
    print(f"Input video         : {INPUT_VIDEO}")
    print(f"Output video        : {OUTPUT_VIDEO}")
    print(f"Output CSV          : {OUTPUT_CSV}")
    print(f"Frames processed    : {frame_id}")
    print(f"Vehicles tracked    : {total_vehicles}")
    print(f"Plates detected     : {total_plates}")
    print(f"OCR results         : {total_ocr}")
    print(f"Plates recognized   : {len(total_recognized)}")
    print(f"Processing FPS      : {avg_fps:.2f}")

if __name__ == "__main__":
    main()
