import csv

path = "outputs/integrated_observations.csv"

with open(path, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("Total OCR observations:", len(rows))

vehicles = {}

for r in rows:
    vid = int(r["vehicle_id"])
    vehicles.setdefault(vid, []).append(
        (
            int(r["frame_id"]),
            r["plate_text"],
            float(r["ocr_confidence"]),
        )
    )

for vid, items in sorted(vehicles.items()):
    print()
    print("Vehicle:", vid)

    for item in items:
        print(
            f"  frame={item[0]:<6} "
            f"plate={item[1]:<15} "
            f"ocr={item[2]:.2f}"
        )
