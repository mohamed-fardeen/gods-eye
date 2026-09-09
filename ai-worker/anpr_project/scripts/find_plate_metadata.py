from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(".")


KEYWORDS = (
    "plate",
    "text",
    "registration",
    "license",
    "number",
    "vehicle",
)


def inspect_csv(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return

        header = rows[0]

        interesting = [
            col
            for col in header
            if any(k in col.lower() for k in KEYWORDS)
        ]

        if interesting:
            print(f"\n[CSV] {path}")
            print(f"Columns: {header}")
            print(f"Potential plate columns: {interesting}")
            print(f"Rows: {len(rows) - 1}")

    except Exception:
        pass


def inspect_json(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        text = json.dumps(data, ensure_ascii=False)

        if any(k in text.lower() for k in KEYWORDS):
            print(f"\n[JSON] {path}")

            if isinstance(data, dict):
                print("Top-level keys:", list(data.keys())[:50])

            elif isinstance(data, list):
                print("Top-level structure: list")
                print("Number of items:", len(data))

    except Exception:
        pass


def inspect_text(path: Path) -> None:
    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if any(k in content.lower() for k in KEYWORDS):
            print(f"\n[TEXT] {path}")
            print(content[:1000])

    except Exception:
        pass


def main() -> None:
    print("Searching project for plate-text metadata...")
    print("=" * 60)

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        # Avoid searching virtual environments and model/cache files.
        if any(
            part.lower() in {
                ".git",
                "venv",
                "__pycache__",
                "runs",
                "models",
                "node_modules",
            }
            for part in path.parts
        ):
            continue

        suffix = path.suffix.lower()

        if suffix == ".csv":
            inspect_csv(path)

        elif suffix == ".json":
            inspect_json(path)

        elif suffix in {".txt", ".yaml", ".yml"}:
            inspect_text(path)

    print()
    print("=" * 60)
    print("Metadata search complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
