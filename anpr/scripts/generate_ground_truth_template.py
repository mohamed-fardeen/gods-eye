import csv
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="outputs/indian_observations.csv")
    parser.add_argument("--output", default="evaluation/ground_truth_indian.csv")
    args = parser.parse_args()

    input_csv = args.input
    output_csv = args.output
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    unique_tracks = set()
    try:
        with open(input_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vehicle_id = row.get("track_id")
                if vehicle_id:
                    unique_tracks.add(int(vehicle_id))
    except FileNotFoundError:
        print(f"Error: {input_csv} not found.")
        sys.exit(1)
        
    sorted_tracks = sorted(list(unique_tracks))
    
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["clip_id", "track_id", "ground_truth_plate", "notes"])
        for track_id in sorted_tracks:
            writer.writerow(["indian_test", track_id, "", ""])
            
    print(f"Extracted {len(sorted_tracks)} unique track IDs.")
    print(f"Template written to {output_csv}")

if __name__ == "__main__":
    main()
