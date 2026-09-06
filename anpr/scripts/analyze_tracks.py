import csv
from collections import defaultdict
import sys

def main():
    tracks = defaultdict(lambda: {"count": 0, "q_sum": 0.0, "ocr_sum": 0.0})
    
    with open("outputs/indian_observations.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = int(row["track_id"])
            q = float(row["quality_score"])
            ocr = float(row["ocr_confidence"])
            
            tracks[tid]["count"] += 1
            tracks[tid]["q_sum"] += q
            tracks[tid]["ocr_sum"] += ocr
            
    good_tracks = []
    for tid, stats in tracks.items():
        if stats["count"] >= 3:
            good_tracks.append({
                "track_id": tid,
                "count": stats["count"],
                "avg_q": stats["q_sum"] / stats["count"],
                "avg_ocr": stats["ocr_sum"] / stats["count"]
            })
            
    good_tracks.sort(key=lambda x: x["count"], reverse=True)
    
    print(f"Total unique tracks: {len(tracks)}")
    print(f"Tracks with >= 3 obs: {len(good_tracks)}")
    print("Top 15 tracks by observation count:")
    for t in good_tracks[:15]:
        print(f"Track {t['track_id']:4d}: {t['count']:2d} obs, avg_q: {t['avg_q']:.3f}, avg_ocr: {t['avg_ocr']:.3f}")
        
    with open("outputs/good_tracks.txt", "w") as f:
        for t in good_tracks:
            f.write(f"{t['track_id']}\n")

if __name__ == "__main__":
    main()
