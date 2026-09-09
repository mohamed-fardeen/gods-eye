from __future__ import annotations

import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ALNUM_RE = re.compile(r"[^A-Z0-9]")


def normalize_text(text: str) -> str:
    return ALNUM_RE.sub("", str(text).upper())


class FineTunedPaddleOCR:
    """
    Adapter around the already-tested fine-tuned PP-OCRv6 model.

    Instead of embedding PaddleOCR's training internals into the video
    pipeline, this adapter invokes PaddleOCR's known-good infer_rec.py
    checkpoint path.

    This is intentionally simple for the 48-hour prototype.
    """

    def __init__(
        self,
        project_root: str = ".",
        checkpoint: str = (
            "models/ocr_ppocrv6_small/best_accuracy"
        ),
        config: str = (
            "configs/PP-OCRv6_small_rec_anpr.yml"
        ),
        character_dict: str = (
            "third_party/PaddleOCR/ppocr/utils/dict/"
            "ppocrv6_dict.txt"
        ),
    ) -> None:

        self.project_root = Path(project_root).resolve()
        self.checkpoint = (
            self.project_root / checkpoint
        )
        self.config = (
            self.project_root / config
        )
        self.character_dict = (
            self.project_root / character_dict
        )

        self.infer_script = (
            self.project_root
            / "third_party"
            / "PaddleOCR"
            / "tools"
            / "infer_rec.py"
        )

        self.output_dir = (
            self.project_root / "outputs" / "video_ocr"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def read_batch(
        self,
        image_paths: list[Path],
    ) -> dict[str, tuple[str, float]]:

        if not image_paths:
            return {}

        with tempfile.TemporaryDirectory() as tmp:

            tmp_dir = Path(tmp)

            for image_path in image_paths:
                target = tmp_dir / image_path.name

                target.write_bytes(
                    image_path.read_bytes()
                )

            prediction_file = (
                self.output_dir
                / "batch_predictions.txt"
            )

            command = [
                sys.executable,
                str(self.infer_script),

                "-c",
                str(self.config),

                "-o",
                "Global.infer_img="
                + str(tmp_dir),

                "Global.checkpoints="
                + str(self.checkpoint),

                "Global.character_dict_path="
                + str(self.character_dict),

                "Global.use_gpu=True",

                "Global.save_res_path="
                + str(prediction_file),
            ]

            subprocess.run(
                command,
                cwd=self.project_root,
                check=True,
            )

            predictions = {}

            if not prediction_file.exists():
                return predictions

            with prediction_file.open(
                "r",
                encoding="utf-8",
            ) as f:

                for line in f:

                    parts = line.rsplit(None, 2)

                    if len(parts) != 3:
                        continue

                    path_text, text, confidence = parts

                    filename = Path(
                        path_text
                    ).name

                    predictions[filename] = (
                        normalize_text(text),
                        float(confidence),
                    )

            return predictions
