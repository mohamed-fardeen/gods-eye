import os
import glob
import shutil
import xml.etree.ElementTree as ET
import csv
import cv2
import random
from collections import defaultdict, Counter

def convert_to_yolo(img_width, img_height, xmin, ymin, xmax, ymax):
    x_center = (xmin + xmax) / 2.0 / img_width
    y_center = (ymin + ymax) / 2.0 / img_height
    width = (xmax - xmin) / img_width
    height = (ymax - ymin) / img_height
    return (max(0, min(1, x_center)), 
            max(0, min(1, y_center)), 
            max(0, min(1, width)), 
            max(0, min(1, height)))

def main():
    raw_dir = 'data/raw'
    # Fallback if sai_dataset is nested
    if os.path.exists(os.path.join(raw_dir, 'sai_dataset')):
        raw_dir = os.path.join(raw_dir, 'sai_dataset')
        
    processed_dir = 'data/processed'
    csv_path = os.path.join(processed_dir, 'sai_master.csv')
    yolo_dir = os.path.join(processed_dir, 'sai_yolo')
    yolo_images_dir = os.path.join(yolo_dir, 'images')
    yolo_labels_dir = os.path.join(yolo_dir, 'labels')
    yaml_path = os.path.join(yolo_dir, 'data.yaml')
    preview_dir = os.path.join(processed_dir, 'sai_yolo_preview')

    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(yolo_images_dir, exist_ok=True)
    os.makedirs(yolo_labels_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    with open(yaml_path, 'w') as f:
        f.write("names:\n  0: license_plate\n")

    all_images = []
    for ext in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'):
        all_images.extend(glob.glob(os.path.join(raw_dir, '**', ext), recursive=True))

    total_images_converted = 0
    total_valid_labels = 0
    total_invalid_annotations = 0
    invalid_boxes = 0
    unique_plate_texts = set()
    images_per_group = Counter()
    example_yolo_labels = []

    csv_rows = []
    csv_header = ['image_path', 'plate_text', 'xmin', 'ymin', 'xmax', 'ymax', 'image_width', 'image_height', 'source_group', 'state']

    preview_candidates = []

    for img_path in all_images:
        rel_path = os.path.relpath(img_path, raw_dir)
        parts = rel_path.split(os.sep)
        group = parts[0] if len(parts) > 0 else 'root'
        state = parts[1] if group == 'State-wise_OLX' and len(parts) > 1 else ''

        base = os.path.splitext(img_path)[0]
        xml_candidates = [base + '.xml', base + '.html']
        xml_path = next((x for x in xml_candidates if os.path.exists(x)), None)

        if not xml_path:
            total_invalid_annotations += 1
            continue

        try:
            tree = ET.parse(xml_path)
            ann = tree.getroot()
            
            size = ann.find('size')
            if size is None:
                continue
            
            w_elem = size.find('width')
            h_elem = size.find('height')
            if w_elem is None or h_elem is None:
                continue
                
            img_width = int(w_elem.text)
            img_height = int(h_elem.text)
            
            if img_width <= 0 or img_height <= 0:
                invalid_boxes += 1
                continue

            objs = ann.findall('object')
            has_valid_plate = False
            
            yolo_lines = []
            
            # Using a sanitized filename for YOLO to avoid collisions if any
            safe_filename = rel_path.replace(os.sep, '_')
            new_img_path = os.path.join(yolo_images_dir, safe_filename)
            new_label_path = os.path.join(yolo_labels_dir, os.path.splitext(safe_filename)[0] + '.txt')

            for o in objs:
                name_elem = o.find('name')
                plate_text = (name_elem.text or '').strip().upper() if name_elem is not None else ''
                b = o.find('bndbox')
                if not b: 
                    continue
                
                xmin_elem = b.find('xmin')
                ymin_elem = b.find('ymin')
                xmax_elem = b.find('xmax')
                ymax_elem = b.find('ymax')
                
                if all(x is not None for x in [xmin_elem, ymin_elem, xmax_elem, ymax_elem]):
                    xmin = int(float(xmin_elem.text))
                    ymin = int(float(ymin_elem.text))
                    xmax = int(float(xmax_elem.text))
                    ymax = int(float(ymax_elem.text))
                    
                    # Validate box
                    if xmax <= xmin or ymax <= ymin or xmin < 0 or ymin < 0 or xmax > img_width or ymax > img_height:
                        invalid_boxes += 1
                        continue
                        
                    has_valid_plate = True
                    total_valid_labels += 1
                    unique_plate_texts.add(plate_text)
                    
                    csv_rows.append([rel_path, plate_text, xmin, ymin, xmax, ymax, img_width, img_height, group, state])
                    
                    yolo_bbox = convert_to_yolo(img_width, img_height, xmin, ymin, xmax, ymax)
                    yolo_line = f"0 {yolo_bbox[0]:.6f} {yolo_bbox[1]:.6f} {yolo_bbox[2]:.6f} {yolo_bbox[3]:.6f}"
                    yolo_lines.append(yolo_line)
                    
                    if len(example_yolo_labels) < 5:
                        example_yolo_labels.append(f"{safe_filename}: {yolo_line}")

            if has_valid_plate:
                # Copy image
                shutil.copy2(img_path, new_img_path)
                # Write YOLO label
                with open(new_label_path, 'w') as f:
                    f.write('\n'.join(yolo_lines) + '\n')
                total_images_converted += 1
                images_per_group[group] += 1
                
                if random.random() < 0.05 and len(preview_candidates) < 10:
                    preview_candidates.append((new_img_path, yolo_lines))
                    
        except Exception as e:
            total_invalid_annotations += 1
            print(f"Error parsing {xml_path}: {e}")

    # Write Master CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)

    # Generate Previews
    for img_p, ylines in preview_candidates:
        img = cv2.imread(img_p)
        if img is not None:
            h, w = img.shape[:2]
            for line in ylines:
                parts = line.split()
                if len(parts) == 5:
                    xc, yc, bw, bh = map(float, parts[1:])
                    xmin = int((xc - bw/2) * w)
                    xmax = int((xc + bw/2) * w)
                    ymin = int((yc - bh/2) * h)
                    ymax = int((yc + bh/2) * h)
                    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            out_path = os.path.join(preview_dir, os.path.basename(img_p))
            cv2.imwrite(out_path, img)

    print("=== Conversion Validation Check ===")
    print(f"Total images converted: {total_images_converted}")
    print(f"Total valid labels (boxes): {total_valid_labels}")
    print(f"Total invalid/missing annotations: {total_invalid_annotations}")
    print(f"Total unique plate texts: {len(unique_plate_texts)}")
    print(f"Number of invalid bounding boxes: {invalid_boxes}")
    print("Images per source group:")
    for grp, cnt in images_per_group.items():
        print(f"  {grp}: {cnt}")
    print("\nExample generated YOLO labels:")
    for ex in example_yolo_labels:
        print(f"  {ex}")
    print(f"\nPreviews saved to: {preview_dir}")
    print(f"Master CSV saved to: {csv_path}")

if __name__ == "__main__":
    main()
