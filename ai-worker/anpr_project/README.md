# Temporal Quality-Aware ANPR — 48-Hour Build Guide

## What's already built (code in this repo)
- `app/quality/quality_scorer.py` — sharpness/brightness/contrast/size scoring. **Tested, working.**
- `app/preprocessing/enhance.py` — perspective correction + CLAHE/denoise/sharpen. **Tested, working.**
- `app/validation/plate_validator.py` — Indian plate regex + safe confusable-char repair. **Tested, working.**
- `app/fusion/temporal_fusion.py` — the core innovation: quality-weighted per-character voting. **Tested against the worked example in the spec — recovers `TN38AB1234` from 5 observations (2 bad) at 95.3% confidence.**
- `app/tracking/tracker.py` — YOLOv8 + ByteTrack vehicle tracking (COCO pretrained, not fine-tuned — see rationale below).
- `app/plate/plate_detector.py` — plate detector wrapper; loads your fine-tuned checkpoint once trained, falls back with a loud warning otherwise.
- `app/ocr/ocr_engine.py` — PaddleOCR (primary) + fast-plate-ocr (comparison/fallback) wrapper.
- `app/pipeline/pipeline.py` — end-to-end orchestration, writes `outputs/track_results.csv`.
- `scripts/check_gpu.py`, `scripts/prepare_dataset.py`, `scripts/synthetic_degrade.py`, `scripts/train_plate_detector.py`
- `evaluation/evaluate.py`, `evaluation/ablation.py`

Everything above runs standalone (each has a `__main__` self-test) and has **no dependency on your dataset**, so you can start on your machine immediately.

---

## Locked architecture decisions (validated against current literature/tools)

| Component | Choice | Why |
|---|---|---|
| Vehicle detector/tracker | YOLOv8n (COCO pretrained) + ByteTrack | Vehicle classes already near-saturated in COCO; fine-tuning wastes GPU budget better spent on plates |
| Plate detector | YOLOv8n/s, **fine-tuned** on Indian plate data | Pretrained COCO has no "license plate" class; Indian plates differ enough (aspect ratio, mounting, two-line plates) that domain fine-tuning is the single highest-value use of your 7-8hr GPU budget |
| OCR | PaddleOCR PP-OCRv4 (mobile), det=False since crop is pre-localized | Strong pretrained accuracy, fast, actively maintained; fine-tune only if MILESTONE 9 baseline measurement justifies it |
| OCR fallback/baseline | fast-plate-ocr (ONNX, plate-specific) | Purpose-built for cropped-plate recognition, useful as Baseline B and a fast fallback |
| Perspective/enhancement | Classical OpenCV (CLAHE, denoise, unsharp, warp) | No learned restoration model — too slow to build/validate in 48h and classical methods are toggleable per-path if they hurt |
| Fusion | Quality-weighted per-character voting + temporal consistency bonus | Directly implements the "stronger observations should dominate" philosophy from the spec |
| Validation | Regex + single safe confusable-character repair only | Never blindly rewrites characters; every repair is logged |

---

## Setup (run these first, in order)

```bash
cd anpr_project
python3 -m venv venv && source venv/bin/activate   # or your preferred env manager
pip install -r requirements.txt
python scripts/check_gpu.py
```

Expected output: `CUDA available: True`, device name containing "5050", ~8GB VRAM.

**Likely errors:**
- `paddlepaddle-gpu` install fails → your CUDA toolkit version doesn't match the pinned wheel. Run `pip install paddlepaddle==2.6.2` (CPU build) instead and pass `use_gpu=False` to `OCREngine` — OCR on crops is cheap enough to run on CPU without hurting your timeline.
- `ultralytics` CUDA mismatch → reinstall `torch`/`torchvision` matching your installed CUDA version from https://pytorch.org (pick the closest CUDA 12.x wheel for RTX 5050).

---

## Data (get this moving in parallel with setup)

python -c "import os,glob,xml.etree.ElementTree as ET,collections,statistics,json; root='data/raw/sai_dataset'; groups=collections.defaultdict(lambda:{'images':0,'valid_xml':0,'plates':0,'unique_plates':set(),'widths':[],'heights':[],'resolutions':collections.Counter(),'states':collections.Counter(),'missing_xml':0}); imgs=glob.glob(os.path.join(root,'**','*.jpg'),recursive=True)+glob.glob(os.path.join(root,'**','*.jpeg'),recursive=True)+glob.glob(os.path.join(root,'**','*.png'),recursive=True); print('TOTAL IMAGES:',len(imgs)); allplates=set(); totalxml=0; totalplates=0; dims=[]; bw=[]; bh=[]; extcounts=collections.Counter(); byfolder=collections.Counter(); statecounts=collections.Counter();\nfor img in imgs:\n d=os.path.relpath(img,root).split(os.sep); group=d[0] if d else 'root'; g=groups[group]; g['images']+=1; byfolder[group]+=1; base=os.path.splitext(img)[0]; candidates=[base+'.xml',base+'.html']; xml=next((x for x in candidates if os.path.exists(x)),None); \n if not xml: g['missing_xml']+=1; continue\n try:\n  tree=ET.parse(xml); ann=tree.getroot(); g['valid_xml']+=1; totalxml+=1; size=ann.find('size'); w=int(size.findtext('width')); h=int(size.findtext('height')); g['resolutions'][f'{w}x{h}']+=1; dims.append((w,h));\n  state=ann.findtext('folder','').strip(); obj=ann.findall('object');\n  for o in obj:\n   t=(o.findtext('name') or '').strip().upper(); b=o.find('bndbox');\n   if not b: continue\n   xmin=int(float(b.findtext('xmin'))); ymin=int(float(b.findtext('ymin'))); xmax=int(float(b.findtext('xmax'))); ymax=int(float(b.findtext('ymax'))); ww=xmax-xmin; hh=ymax-ymin;\n   if ww>0 and hh>0: g['plates']+=1; totalplates+=1; g['unique_plates'].add(t); allplates.add(t); g['widths'].append(ww); g['heights'].append(hh); bw.append(ww); bh.append(hh)\n except Exception as e: extcounts[str(e)]+=1\nprint('\\n=== SUMMARY ==='); print('Groups:',dict(byfolder)); print('Total valid XML:',totalxml); print('Total annotated plates:',totalplates); print('Unique plate texts:',len(allplates));\nfor k,g in groups.items(): print(f'\\n[{k}]'); print('Images:',g['images']); print('Valid annotations:',g['valid_xml']); print('Missing annotation:',g['missing_xml']); print('Plates:',g['plates']); print('Unique plate texts:',len(g['unique_plates'])); print('Top resolutions:',g['resolutions'].most_common(10));\n if g['widths']: print('Plate width px: min',min(g['widths']),'avg',round(statistics.mean(g['widths']),1),'max',max(g['widths'])); print('Plate height px: min',min(g['heights']),'avg',round(statistics.mean(g['heights']),1),'max',max(g['heights']))\nprint('\\nOverall plate width px: min',min(bw) if bw else None,'avg',round(statistics.mean(bw),1) if bw else None,'max',max(bw) if bw else None); print('Overall plate height px: min',min(bh) if bh else None,'avg',round(statistics.mean(bh),1) if bh else None,'max',max(bh) if bh else None); print('\\nXML parse errors:',sum(extcounts.values()))"
. Put it at:
```
data/raw/plate_detection/images/*.jpg
data/raw/plate_detection/labels/*.txt   (YOLO format)
```
If it's not already YOLO format, most Roboflow exports let you choose "YOLOv8" as the export format directly — do that instead of writing a converter.

Then:
```bash
python scripts/prepare_dataset.py --raw_dir data/raw/plate_detection --out_dir data/processed/plate_detection
```
This deduplicates, does an identity-aware 80/10/10 split, and writes `data.yaml`.

**Check the printed split summary** — if train is much smaller than the ~8k-10k target range, that's your first real signal to look for a second dataset to merge (dedupe again after merging, don't just concatenate).

---

## 48-Hour Schedule

| Hours | Task | GPU/CPU | Critical path? | Runs in parallel with |
|---|---|---|---|---|
| 0-1 | Env setup, GPU check, project structure | CPU | Yes | — |
| 1-3 | Download + `prepare_dataset.py` | CPU | Yes | — |
| 3-4 | Sanity-check dataset (plot a few boxes, check label sanity) | CPU | Yes | — |
| **4-12** | **`train_plate_detector.py` — the 7-8hr training run** | **GPU** | **Yes** | Everything below |
| 4-6 | Wire up `quality_scorer`, `enhance`, `ocr_engine`, test on manually cropped sample plates | CPU | No | Training |
| 6-8 | Wire up `plate_validator`, `temporal_fusion` (already tested — verify against your own examples) | CPU | No | Training |
| 8-10 | Build `tracker.py` integration, test vehicle tracking on a sample CCTV clip (plate detector fallback warning expected here) | CPU/GPU-light | No | Training |
| 10-12 | Build `pipeline.py` end-to-end wiring, dry run with fallback detector | CPU/GPU-light | No | Training |
| **12-13** | **Swap in trained checkpoint** (`cp models/plate_detector/weights/best.pt models/plate_detector_best.pt`), re-run pipeline | GPU | Yes | — |
| 13-16 | Baseline OCR measurement (MILESTONE 9): run pretrained PaddleOCR on real crops, decide fine-tune or not | GPU-light | Yes | — |
| 16-18 | `synthetic_degrade.py` on train crops (only if OCR fine-tuning is justified) | CPU | No | — |
| 18-24 | (Optional) OCR fine-tuning, if justified | GPU | No | Report writing |
| 18-26 | Build ground_truth.csv by hand-labeling a held-out test clip (this is your real accuracy ceiling — don't skip it) | CPU | Yes | — |
| 26-32 | Run `evaluate.py`, fix the single worst failure mode only (MILESTONE 22) | CPU | Yes | — |
| 32-36 | Run `ablation.py` — confirms fusion actually helps vs baselines | CPU | Yes | — |
| 36-40 | Adverse-condition test set assembly (real + labeled synthetic, clearly tagged) | CPU | Yes | — |
| 40-44 | Streamlit demo UI (video → boxes → quality → OCR candidates → fused result → confidence) | CPU | No | — |
| 44-46 | Record the "5 frames → fused result" demo clip from the spec | CPU | Yes | — |
| 46-48 | Write up results with the SCIENTIFIC HONESTY breakdown (demonstrated / literature-supported / target / not demonstrated) | CPU | Yes | — |

## Critical path (in priority order)
1. Dataset is actually usable (check split_summary.json isn't near-empty)
2. Detector fine-tuning converges (watch train mAP50 in Ultralytics logs — should clear ~0.7+ on val)
3. OCR reads clean crops correctly at all (sanity check before blaming fusion for OCR errors)
4. Track→plate association doesn't drop vehicles (log `len(buffers)` vs actual vehicle count in test clip)
5. Fusion measurably beats single-frame baseline (this is what `ablation.py` proves or disproves)
6. Ground truth labeling is accurate (a wrong label invalidates everything downstream — double check a sample)

## Fallbacks (already wired where possible)
- Detector fine-tuning poor → `plate_detector.py` already falls back to pretrained + loud warning; consider a public pretrained Indian-plate YOLO checkpoint from Roboflow Universe as a stronger fallback than raw COCO.
- OCR fine-tuning doesn't help → skip it, `ocr_engine.py` already defaults to pretrained-only.
- Tracking unstable → reduce to plate-level temporal aggregation over an N-frame sliding window instead of full track association (would need a small change in `pipeline.py`'s buffering — flag if you hit this).
- Enhancement hurts a condition → toggle off individual stages in `enhance_for_ocr()`, each stage is isolated.
- OOM on GPU → drop `--batch` to 8, then `--imgsz` to 512, in `train_plate_detector.py` (in that order, per RTX 5050 8GB guidance in the script's docstring).

## Running the pipeline
```bash
python -m app.pipeline.pipeline --video path/to/test_clip.mp4 --output outputs/track_results.csv
python evaluation/evaluate.py --gt evaluation/ground_truth.csv --pred outputs/track_results.csv
```

## Scientific honesty checklist for your final report
- **Demonstrated**: only numbers that came out of `evaluate.py` on your labeled test set.
- **Literature-supported**: multi-frame fusion and quality-aware selection are established ideas (cite general ANPR/temporal-fusion literature) — your contribution is the specific weighting scheme, not the concept.
- **Target**: the SIH >90% figure — state it as the goal, not an achieved result, unless `evaluate.py`'s Overall row actually shows it.
- **Not demonstrated**: any condition with "NO DATA" in the evaluation report, and anything only tested via `synthetic_degrade.py` (label it synthetic, not real-world).
