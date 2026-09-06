"""
Video inspection script — reports key properties and samples frames
for visual assessment.
"""
import cv2
import os
import sys
import numpy as np

def inspect_video(video_path: str, sample_count: int = 20):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open {video_path}", file=sys.stderr)
        sys.exit(1)

    fps     = cap.get(cv2.CAP_PROP_FPS)
    width   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames= int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration= n_frames / fps if fps > 0 else 0.0

    print("=" * 60)
    print("VIDEO INSPECTION REPORT")
    print("=" * 60)
    print(f"Path         : {video_path}")
    print(f"Resolution   : {width} x {height}")
    print(f"FPS          : {fps:.3f}")
    print(f"Total Frames : {n_frames}")
    print(f"Duration     : {duration:.2f} s  ({duration/60:.2f} min)")

    # Sample frames for brightness / blur analysis
    brightness_vals = []
    blur_vals = []
    sample_interval = max(1, n_frames // sample_count)

    out_dir = "outputs/indian_inspection_frames"
    os.makedirs(out_dir, exist_ok=True)

    saved = 0
    for i in range(0, n_frames, sample_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_vals.append(float(gray.mean()))
        # Laplacian variance — proxy for sharpness
        blur_vals.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
        if saved < 5:
            cv2.imwrite(f"{out_dir}/sample_{i:06d}.jpg", frame)
            saved += 1

    cap.release()

    print(f"\nBrightness   : mean={np.mean(brightness_vals):.1f}  "
          f"min={np.min(brightness_vals):.1f}  max={np.max(brightness_vals):.1f}")
    print(f"Sharpness    : mean={np.mean(blur_vals):.1f}  "
          f"min={np.min(blur_vals):.1f}  max={np.max(blur_vals):.1f}")
    print(f"Sample frames: saved to {out_dir}/")
    print()

    # Brightness interpretation
    mean_bright = np.mean(brightness_vals)
    mean_blur = np.mean(blur_vals)
    if mean_bright < 60:
        lighting = "LOW (night/underexposed)"
    elif mean_bright > 180:
        lighting = "HIGH (overexposed/glare risk)"
    else:
        lighting = "GOOD (daylight)"

    if mean_blur < 50:
        sharpness = "BLURRY (motion blur / defocus likely)"
    elif mean_blur < 200:
        sharpness = "MODERATE"
    else:
        sharpness = "SHARP"

    print(f"Lighting     : {lighting}")
    print(f"Sharpness    : {sharpness}")
    print("=" * 60)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/test/indian_test.mp4"
    inspect_video(path)
