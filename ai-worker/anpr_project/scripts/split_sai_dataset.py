import os
import shutil
import csv
import json
import random
from collections import defaultdict
from PIL import Image
import imagehash

def main():
    random.seed(42)
    processed_dir = 'data/processed'
    master_csv = os.path.join(processed_dir, 'sai_master.csv')
    yolo_dir = os.path.join(processed_dir, 'sai_yolo')
    yolo_images_dir = os.path.join(yolo_dir, 'images')
    yolo_labels_dir = os.path.join(yolo_dir, 'labels')
    
    split_dir = os.path.join(processed_dir, 'sai_split')
    splits = ['train', 'val', 'test']
    
    # Create directories
    if os.path.exists(split_dir):
        shutil.rmtree(split_dir)
    os.makedirs(split_dir)
    
    for sp in splits:
        os.makedirs(os.path.join(split_dir, sp, 'images'))
        os.makedirs(os.path.join(split_dir, sp, 'labels'))

    # Load master CSV
    # Columns: ['image_path', 'plate_text', 'xmin', 'ymin', 'xmax', 'ymax', 'image_width', 'image_height', 'source_group', 'state']
    all_rows = []
    with open(master_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)

    print(f"Loaded {len(all_rows)} rows from master CSV.")

    # Identify YOLO files
    # The image name in yolo_dir is rel_path.replace(os.sep, '_')
    for row in all_rows:
        safe_filename = row['image_path'].replace(os.sep, '_')
        row['yolo_image_name'] = safe_filename
        row['yolo_label_name'] = os.path.splitext(safe_filename)[0] + '.txt'

    # Deduplication
    print("Computing perceptual hashes for deduplication...")
    hashes = {}
    duplicates = []
    unique_rows = []
    
    for i, row in enumerate(all_rows):
        img_path = os.path.join(yolo_images_dir, row['yolo_image_name'])
        try:
            with Image.open(img_path) as img:
                h = str(imagehash.phash(img))
                if h in hashes:
                    duplicates.append(row)
                else:
                    hashes[h] = row
                    unique_rows.append(row)
        except Exception as e:
            print(f"Error hashing {img_path}: {e}")
            # If error, just keep it
            unique_rows.append(row)
            
    print(f"Found {len(duplicates)} duplicate images.")
    print(f"Remaining unique images: {len(unique_rows)}")
    
    # Group by plate_text to prevent leakage
    plate_groups = defaultdict(list)
    for row in unique_rows:
        plate = row['plate_text']
        plate_groups[plate].append(row)

    # Sort groups by size descending to make greedy assignment work well
    sorted_groups = sorted(plate_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Target proportions
    target_props = {'train': 0.8, 'val': 0.1, 'test': 0.1}
    target_counts = {k: v * len(unique_rows) for k, v in target_props.items()}
    current_counts = {'train': 0, 'val': 0, 'test': 0}
    
    split_assignment = {} # image_path -> split
    
    for plate, rows in sorted_groups:
        # Find which split is furthest from its target proportion
        # i.e., max(target - current)
        best_split = max(splits, key=lambda s: target_counts[s] - current_counts[s])
        
        for r in rows:
            split_assignment[r['image_path']] = best_split
        
        current_counts[best_split] += len(rows)

    print(f"Target counts: {target_counts}")
    print(f"Actual counts: {current_counts}")
    
    # Write splits
    split_rows = {'train': [], 'val': [], 'test': []}
    plate_counts = {'train': set(), 'val': set(), 'test': set()}
    
    for row in unique_rows:
        sp = split_assignment[row['image_path']]
        split_rows[sp].append(row)
        plate_counts[sp].add(row['plate_text'])
        
        # Copy image and label
        src_img = os.path.join(yolo_images_dir, row['yolo_image_name'])
        src_lbl = os.path.join(yolo_labels_dir, row['yolo_label_name'])
        
        dst_img = os.path.join(split_dir, sp, 'images', row['yolo_image_name'])
        dst_lbl = os.path.join(split_dir, sp, 'labels', row['yolo_label_name'])
        
        # Handle Windows long paths
        abs_src_img = os.path.abspath(src_img)
        abs_dst_img = os.path.abspath(dst_img)
        abs_src_lbl = os.path.abspath(src_lbl)
        abs_dst_lbl = os.path.abspath(dst_lbl)
        
        if os.name == 'nt':
            abs_src_img = '\\\\?\\' + abs_src_img
            abs_dst_img = '\\\\?\\' + abs_dst_img
            abs_src_lbl = '\\\\?\\' + abs_src_lbl
            abs_dst_lbl = '\\\\?\\' + abs_dst_lbl
            
        shutil.copy2(abs_src_img, abs_dst_img)
        shutil.copy2(abs_src_lbl, abs_dst_lbl)
        
    # Write split CSVs
    fieldnames = all_rows[0].keys()
    for sp in splits:
        with open(os.path.join(split_dir, f"{sp}.csv"), 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(split_rows[sp])
            
    # Write data.yaml
    with open(os.path.join(split_dir, 'data.yaml'), 'w') as f:
        f.write(f"train: ../train/images\n")
        f.write(f"val: ../val/images\n")
        f.write(f"test: ../test/images\n\n")
        f.write("names:\n  0: license_plate\n")

    # Consistency Check
    consistency_passed = True
    for sp in splits:
        imgs = os.listdir(os.path.join(split_dir, sp, 'images'))
        lbls = os.listdir(os.path.join(split_dir, sp, 'labels'))
        for img in imgs:
            if os.path.splitext(img)[0] + '.txt' not in lbls:
                consistency_passed = False
                print(f"ERROR: Missing label for {img} in {sp} split!")
    
    if consistency_passed:
        print("\nConsistency check passed: Every image has exactly one corresponding label in all splits.")
        
    # Summary
    summary = {
        'original_image_count': len(all_rows),
        'duplicate_count': len(duplicates),
        'final_image_count': len(unique_rows),
        'train_count': len(split_rows['train']),
        'val_count': len(split_rows['val']),
        'test_count': len(split_rows['test']),
        'unique_plates': {
            'total': len(plate_groups),
            'train': len(plate_counts['train']),
            'val': len(plate_counts['val']),
            'test': len(plate_counts['test'])
        },
        'leakage_risk': "Minimal. Images are grouped by plate_text. Exact phash duplicates removed.",
        'consistency_passed': consistency_passed
    }
    
    with open(os.path.join(split_dir, 'split_summary.json'), 'w') as f:
        json.dump(summary, f, indent=4)
        
    print("\n=== SPLIT SUMMARY ===")
    print(f"Original image count: {summary['original_image_count']}")
    print(f"Duplicate count removed: {summary['duplicate_count']}")
    print(f"Final image count: {summary['final_image_count']}")
    print(f"Train count: {summary['train_count']} ({summary['train_count']/summary['final_image_count']*100:.1f}%)")
    print(f"Validation count: {summary['val_count']} ({summary['val_count']/summary['final_image_count']*100:.1f}%)")
    print(f"Test count: {summary['test_count']} ({summary['test_count']/summary['final_image_count']*100:.1f}%)")
    print("\nUnique plate counts:")
    print(f"  Train: {summary['unique_plates']['train']}")
    print(f"  Val: {summary['unique_plates']['val']}")
    print(f"  Test: {summary['unique_plates']['test']}")
    print(f"\nRemaining leakage risks: {summary['leakage_risk']}")

if __name__ == '__main__':
    main()
