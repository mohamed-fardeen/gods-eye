"""
Indian license plate structural validation.

Standard format (IND, non-BH-series civilian plates):
    SS NN LL NNNN
    SS   = state code, 2 letters (e.g. TN, KA, DL, MH)
    NN   = RTO district code, 2 digits
    LL   = series, 1-2 letters (sometimes absent, sometimes 1 letter)
    NNNN = 4-digit unique number

Also supports the newer BH-series format:
    NN BH NNNN LL   (e.g. 22 BH 1234 AB)

This module does NOT invent characters. It only:
  1. checks whether a candidate string is structurally plausible, and
  2. offers *safe* commonly-confused-character correction ONLY when it turns
     an implausible string into a plausible one with a single substitution,
     and only among a small whitelist of visually-confusable pairs learned
     from OCR error analysis (0/O, 1/I, 8/B, 5/S, 2/Z).

This is deliberately conservative: MILESTONE 17 explicitly forbids "blindly
replacing characters". Every correction is logged so it can be audited.
"""

from dataclasses import dataclass
import re

STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP", "JH", "KA", "KL",
    "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB", "RJ", "SK", "TN", "TS",
    "TR", "UP", "UK", "WB", "AN", "CH", "DN", "DD", "DL", "JK", "LA", "LD", "PY",
}

STANDARD_RE = re.compile(r"^([A-Z]{2})(\d{2})([A-Z]{0,2})(\d{4})$")
BH_RE = re.compile(r"^(\d{2})(BH)(\d{4})([A-Z]{2})$")

# Visually-confusable character pairs commonly produced by OCR on plates.
# Used ONLY for single-substitution repair attempts, never multi-character.
CONFUSION_PAIRS = [("0", "O"), ("1", "I"), ("8", "B"), ("5", "S"), ("2", "Z")]


@dataclass
class ValidationResult:
    is_valid: bool
    plate_format: str | None  # "standard" | "bh_series" | None
    corrected_text: str | None
    correction_applied: bool
    reason: str


def _structurally_valid(text: str) -> tuple[bool, str | None]:
    m = STANDARD_RE.match(text)
    if m and m.group(1) in STATE_CODES:
        return True, "standard"
    if BH_RE.match(text):
        return True, "bh_series"
    return False, None


def _try_single_substitution_repair(text: str) -> str | None:
    """Try each confusion-pair swap at each position; return the first
    result that becomes structurally valid. None if no single swap fixes it."""
    for i, ch in enumerate(text):
        for a, b in CONFUSION_PAIRS:
            if ch == a or ch == b:
                other = b if ch == a else a
                candidate = text[:i] + other + text[i + 1:]
                valid, _ = _structurally_valid(candidate)
                if valid:
                    return candidate
    return None


def validate_plate(raw_text: str) -> ValidationResult:
    text = re.sub(r"[^A-Z0-9]", "", raw_text.upper())

    valid, fmt = _structurally_valid(text)
    if valid:
        return ValidationResult(True, fmt, text, False, "structurally valid as-is")

    repaired = _try_single_substitution_repair(text)
    if repaired:
        valid2, fmt2 = _structurally_valid(repaired)
        return ValidationResult(
            True, fmt2, repaired, True,
            f"repaired via single confusable-character substitution ({text} -> {repaired})",
        )

    return ValidationResult(False, None, None, False, "not structurally plausible; no safe repair found")


if __name__ == "__main__":
    tests = ["TN38AB1234", "TN38A81234", "KA05MH1234", "22BH1234AB", "XX99ZZ0000"]
    for t in tests:
        print(t, "->", validate_plate(t))
