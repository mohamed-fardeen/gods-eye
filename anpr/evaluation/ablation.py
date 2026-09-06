"""
PRELIMINARY ENGINEERING ABLATION
FOREIGN-VEHICLE TEST VIDEO
NOT FINAL INDIAN ANPR ACCURACY

A: SINGLE FRAME OCR
B: BEST FRAME OCR
C: MULTI-FRAME OCR
D: MULTI-FRAME + QUALITY
E: MULTI-FRAME + QUALITY + VALIDATION
"""

import argparse
import json
import csv
import time
import os
import cv2
from collections import defaultdict
from anpr.fusion.temporal_fusion import (
    ObservationRecord, 
    fuse_observations, 
    _strategy_char_vote
)
from anpr.validation.plate_validator import validate_plate
from anpr.quality.quality_scorer import score_plate_crop
from evaluation.evaluate import load_csv, char_accuracy, levenshtein

def normalize(text: str) -> str:
    if not text:
        return ""
    return "".join(c for c in text.upper() if c.isalnum())

def variant_A_single_frame(observations: list[ObservationRecord]) -> tuple[str, float]:
    if not observations:
        return "", 0.0
    return observations[-1].normalized_text or "", observations[-1].ocr_confidence

def variant_B_best_frame(observations: list[ObservationRecord]) -> tuple[str, float]:
    if not observations:
        return "", 0.0
    best = max(observations, key=lambda o: o.quality_score)
    return best.normalized_text or "", best.ocr_confidence

def variant_C_unweighted_vote(observations: list[ObservationRecord]) -> tuple[str, float]:
    if not observations:
        return "", 0.0
    flat = [
        ObservationRecord(
            frame_id=o.frame_id, 
            track_id=o.track_id, 
            raw_text=o.raw_text, 
            normalized_text=normalize(o.raw_text),
            ocr_confidence=1.0, 
            quality_score=1.0, 
            detector_confidence=1.0,
            timestamp=0.0
        ) for o in observations
    ]
    valid_obs = [o for o in flat if o.normalized_text]
    if not valid_obs:
        return "", 0.0
    text, conf = _strategy_char_vote(valid_obs)
    return text, conf

def variant_D_quality_weighted(observations: list[ObservationRecord]) -> tuple[str, float]:
    if not observations:
        return "", 0.0
    valid_obs = [o for o in observations if o.normalized_text]
    if not valid_obs:
        return "", 0.0
    text, conf = _strategy_char_vote(valid_obs)
    return text, conf

def variant_E_full_pipeline(observations: list[ObservationRecord]) -> tuple[str, float, dict]:
    if not observations:
        return "", 0.0, {}
    result = fuse_observations(observations)
    
    # Extract provenance
    provenance = {
        "decision": result.decision,
        "supporting_obs_count": result.supporting_obs_count,
        "best_evidence_frame": result.best_evidence_frame,
    }
    return result.fused_text or "", result.confidence, provenance

VARIANTS = {
    "A": variant_A_single_frame,
    "B": variant_B_best_frame,
    "C": variant_C_unweighted_vote,
    "D": variant_D_quality_weighted,
    "E": variant_E_full_pipeline,
}

def analyze_error(true_plate: str, pred: str, observations: list[ObservationRecord], prev_pred: str = None) -> str:
    if not pred:
        if len(observations) < 3:
            return "insufficient observations"
        return "unreadable"
    
    if len(true_plate) == len(pred):
        return "OCR character confusion"
        
    return "unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", default="outputs/integrated_observations.csv")
    parser.add_argument("--gt", default="evaluation/ground_truth.csv")
    args = parser.parse_args()

    # Load Ground Truth
    gt_rows = {}
    total_gt_tracks = 0
    excluded_tracks = 0
    try:
        for r in load_csv(args.gt):
            total_gt_tracks += 1
            notes = r.get("notes", "")
            if "unreliable ground truth" in notes.lower():
                excluded_tracks += 1
                continue
            plate = r.get("ground_truth_plate", "").strip().upper()
            if not plate:
                excluded_tracks += 1
                continue
            gt_rows[int(r["track_id"])] = plate
    except FileNotFoundError:
        print(f"Error: {args.gt} not found.")
        return

    # Load Observations
    raw_obs = defaultdict(list)
    obs_source = args.observations
    try:
        with open(args.observations, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                track_id = int(row["vehicle_id"])
                if track_id not in gt_rows:
                    continue
                
                frame_id = int(row["frame_id"])
                text = row["plate_text"]
                ocr_conf = float(row["ocr_confidence"]) if row["ocr_confidence"] else 0.0
                det_conf = float(row["plate_detection_confidence"]) if row["plate_detection_confidence"] else 0.0
                
                # Try to compute quality score from crop
                quality = 1.0
                crop_path = f"outputs/integrated_plate_crops/frame_{frame_id:06d}_vehicle_{track_id}_plate_0.jpg"
                if os.path.exists(crop_path):
                    crop = cv2.imread(crop_path)
                    if crop is not None and crop.size > 0:
                        q_res = score_plate_crop(crop)
                        quality = q_res.overall
                
                obs = ObservationRecord(
                    frame_id=frame_id,
                    track_id=track_id,
                    raw_text=text,
                    normalized_text=normalize(text),
                    ocr_confidence=ocr_conf,
                    quality_score=quality,
                    detector_confidence=det_conf,
                    timestamp=0.0
                )
                raw_obs[track_id].append(obs)
    except FileNotFoundError:
        print(f"Error: {args.observations} not found.")
        return

    scores = {name: {"exact": 0, "total": 0, "unreadable": 0, "char_acc": [], "cer": [], "cpu_time": 0.0} for name in VARIANTS}
    
    tracks_evaluated = 0
    tracks_with_1 = 0
    tracks_with_2plus = 0
    
    track_predictions = {}
    
    for track_id, true_plate in gt_rows.items():
        if track_id not in raw_obs:
            continue
            
        observations = raw_obs[track_id]
        obs_count = len(observations)
        if obs_count == 0:
            continue
            
        tracks_evaluated += 1
        if obs_count == 1:
            tracks_with_1 += 1
        else:
            tracks_with_2plus += 1

        track_preds = {}
        for name, fn in VARIANTS.items():
            t0 = time.perf_counter()
            if name == "E":
                pred, conf, prov = fn(observations)
            else:
                pred, conf = fn(observations)
            t1 = time.perf_counter()
            
            scores[name]["cpu_time"] += (t1 - t0)
            scores[name]["total"] += 1
            
            if not pred:
                scores[name]["unreadable"] += 1
                scores[name]["char_acc"].append(0.0)
                scores[name]["cer"].append(1.0)
                track_preds[name] = {"pred": "UNREADABLE", "status": "UNREADABLE", "conf": conf}
            else:
                if pred == true_plate:
                    scores[name]["exact"] += 1
                    status = "CORRECT"
                else:
                    status = "WRONG"
                
                scores[name]["char_acc"].append(char_accuracy(true_plate, pred))
                cer = levenshtein(true_plate, pred) / max(len(true_plate), 1)
                scores[name]["cer"].append(cer)
                track_preds[name] = {"pred": pred, "status": status, "conf": conf}
                
        track_predictions[track_id] = {"true": true_plate, "preds": track_preds}

    if tracks_evaluated == 0:
        print("No matching track_ids between observations and ground_truth with valid plates.")
        return

    print("==================================================")
    print("PRELIMINARY ENGINEERING ABLATION")
    print("FOREIGN-VEHICLE TEST VIDEO")
    print("NOT FINAL INDIAN ANPR ACCURACY")
    print("==================================================")
    print(f"Total ground-truth tracks : {total_gt_tracks}")
    print(f"Labeled tracks            : {total_gt_tracks - excluded_tracks}")
    print(f"Excluded/unlabeled tracks : {excluded_tracks}")
    print(f"Evaluated tracks          : {tracks_evaluated}")
    print(f"Observation source used   : {obs_source}")
    print(f"Tracks with 1 obs         : {tracks_with_1}")
    print(f"Tracks with 2+ obs        : {tracks_with_2plus}")
    
    print("\n==================================================")
    print("ERROR ANALYSIS (Track-by-Track)")
    print("==================================================")
    for tid, data in track_predictions.items():
        print(f"Track {tid:03d} | GT: {data['true']}")
        preds = data['preds']
        for v in ["A", "B", "C", "D", "E"]:
            print(f"  {v}: {preds[v]['pred']:<12} [{preds[v]['status']:<10}] (Conf: {preds[v]['conf']:.3f})")
            
        a_stat = preds['A']['status']
        b_stat = preds['B']['status']
        c_stat = preds['C']['status']
        d_stat = preds['D']['status']
        e_stat = preds['E']['status']
        
        changes = []
        if a_stat != e_stat:
            if a_stat == "WRONG" and e_stat == "CORRECT": changes.append("A->E corrected")
            elif a_stat == "CORRECT" and e_stat == "WRONG": changes.append("A->E degraded")
        
        if preds['A']['pred'] != preds['B']['pred']: changes.append("A->B changed")
        if preds['B']['pred'] != preds['C']['pred']: changes.append("B->C changed")
        if preds['C']['pred'] != preds['D']['pred']: changes.append("C->D changed")
        if preds['D']['pred'] != preds['E']['pred']: changes.append("D->E changed")
        
        if changes:
            print(f"  Changes: {', '.join(changes)}")
        print()

    print("==================================================")
    print("A/B/C/D/E RESULT TABLE")
    print("==================================================")
    print(f"{'Strategy':<10}{'Evaluated':<12}{'Exact Match':>15}{'Char Acc':>15}{'CER':>15}{'Unreadable %':>15}")
    
    for name, s in scores.items():
        total = s["total"]
        exact_pct = (s["exact"] / total * 100) if total else 0.0
        char_pct = (sum(s["char_acc"]) / len(s["char_acc"]) * 100) if s["char_acc"] else 0.0
        cer_pct = (sum(s["cer"]) / len(s["cer"]) * 100) if s["cer"] else 0.0
        unread_pct = (s["unreadable"] / total * 100) if total else 0.0
        
        print(f"{name:<10}{total:<12}{exact_pct:>14.1f}%{char_pct:>14.1f}%{cer_pct:>14.1f}%{unread_pct:>14.1f}%")
        
    print("\n--------------------------------------------------")
    a_exact = (scores["A"]["exact"] / scores["A"]["total"] * 100) if scores["A"]["total"] else 0
    e_exact = (scores["E"]["exact"] / scores["E"]["total"] * 100) if scores["E"]["total"] else 0
    
    abs_imp = e_exact - a_exact
    rel_imp = (abs_imp / a_exact * 100) if a_exact > 0 else float('inf')
    
    print(f"A -> E absolute improvement: {abs_imp:+.1f}%")
    if a_exact > 0:
        print(f"A -> E relative improvement: {rel_imp:+.1f}%")
    else:
        print("A -> E relative improvement: N/A")
        
    print("\n* Note: E may degrade on foreign plates due to strict Indian formatting validation.")
    
    print("\n==================================================")
    print("PERFORMANCE (CPU Fusion Time)")
    print("==================================================")
    for name in ["C", "D", "E"]:
        avg_time_ms = (scores[name]["cpu_time"] / tracks_evaluated * 1000) if tracks_evaluated else 0
        print(f"Strategy {name}: {avg_time_ms:.2f} ms / track")
        
    print("\n==================================================")
    print("RECOMMENDED NEXT STEP")
    print("==================================================")
    print("Evaluate the specific failure cases in E. If E rejects valid foreign plates, it confirms the validation layer is restrictive by design. Once ready, run this same ablation on a purely Indian test video dataset.")

if __name__ == "__main__":
    main()
