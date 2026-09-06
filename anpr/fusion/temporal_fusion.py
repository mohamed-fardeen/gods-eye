"""
Temporal quality-weighted evidence fusion.

Core idea (see MASTER PROMPT "CORE SYSTEM PHILOSOPHY"): a vehicle track
produces multiple plate observations over time. Instead of trusting any
single frame, we weight each OCR candidate by how trustworthy its source
observation was, then let weighted votes decide the final string —
per character position, not just per whole string, since two "wrong"
reads can still agree on most characters.

Weight per observation = quality * ocr_confidence * detection_confidence
(temporal consistency bonus is applied after an initial pass, once we know
which observations agree with the emerging consensus).

This is a re-application of known ideas (temporal/multi-observation fusion,
confusable-character voting) — not a novel algorithm class. The specific
combination (quality-weighted, per-character voting, confusable-aware,
explicit reject band) is what MILESTONE 16 calls "our contribution".
"""

from dataclasses import dataclass, field
from collections import defaultdict

from anpr.validation.plate_validator import validate_plate, ValidationResult


@dataclass
class Observation:
    frame_id: int
    text: str                 # cleaned OCR text for this observation
    ocr_confidence: float      # 0-1, from OCR engine
    quality_score: float       # 0-1, from quality_scorer
    detection_confidence: float = 1.0  # 0-1, from detector, default 1.0 if unknown

    @property
    def weight(self) -> float:
        return self.ocr_confidence * self.quality_score * self.detection_confidence


@dataclass
class FusionResult:
    final_plate: str | None
    confidence: float          # 0-1
    status: str                # "ACCEPT" | "NEEDS_MORE_EVIDENCE" | "UNREADABLE"
    evidence_frame_ids: list[int]
    num_observations: int
    validation: ValidationResult | None


# Confidence thresholds. Tune against evaluation/ results (MILESTONE 18/22).
HIGH_CONFIDENCE = 0.75
MEDIUM_CONFIDENCE = 0.45
MIN_OBSERVATIONS_FOR_ACCEPT = 2


def _char_vote(observations: list[Observation]) -> tuple[str, float]:
    """
    Per-position weighted character voting across observations of equal
    length (the modal length). Observations with a different length than
    the modal length are excluded from character voting (they likely have
    a missed/extra character) but still contribute later during
    whole-string confidence estimation.

    Returns (voted_string, mean_position_agreement).
    """
    if not observations:
        return "", 0.0

    length_weights: dict[int, float] = defaultdict(float)
    for obs in observations:
        length_weights[len(obs.text)] += obs.weight
    modal_length = max(length_weights, key=length_weights.get)

    same_length = [o for o in observations if len(o.text) == modal_length]
    if not same_length:
        # fall back to the single highest-weight observation
        best = max(observations, key=lambda o: o.weight)
        return best.text, best.weight

    voted_chars = []
    position_agreements = []
    for pos in range(modal_length):
        votes: dict[str, float] = defaultdict(float)
        for obs in same_length:
            votes[obs.text[pos]] += obs.weight
        winner_char = max(votes, key=votes.get)
        total_weight = sum(votes.values())
        agreement = votes[winner_char] / total_weight if total_weight > 0 else 0.0
        voted_chars.append(winner_char)
        position_agreements.append(agreement)

    voted_string = "".join(voted_chars)
    mean_agreement = sum(position_agreements) / len(position_agreements)
    return voted_string, mean_agreement


def fuse_observations(observations: list[Observation]) -> FusionResult:
    if not observations:
        return FusionResult(None, 0.0, "UNREADABLE", [], 0, None)

    voted_string, mean_agreement = _char_vote(observations)

    # Overall confidence blends: character-position agreement, mean
    # observation weight, and a small bonus for having multiple
    # corroborating observations (temporal consistency).
    mean_weight = sum(o.weight for o in observations) / len(observations)
    n_obs_bonus = min(len(observations) / 5.0, 1.0) * 0.1  # up to +0.1 for 5+ obs
    raw_confidence = 0.6 * mean_agreement + 0.3 * mean_weight + n_obs_bonus
    raw_confidence = min(raw_confidence, 1.0)

    validation = validate_plate(voted_string) if voted_string else None
    final_text = validation.corrected_text if (validation and validation.is_valid) else voted_string

    # Validation success nudges confidence up; failure nudges it down —
    # structural plausibility is real signal, not just a filter.
    if validation and validation.is_valid:
        confidence = min(raw_confidence + 0.1, 1.0)
    else:
        confidence = max(raw_confidence - 0.15, 0.0)

    evidence_ids = [o.frame_id for o in observations]

    if confidence >= HIGH_CONFIDENCE and len(observations) >= MIN_OBSERVATIONS_FOR_ACCEPT and validation and validation.is_valid:
        status = "ACCEPT"
    elif confidence >= MEDIUM_CONFIDENCE:
        status = "NEEDS_MORE_EVIDENCE"
    else:
        status = "UNREADABLE"

    return FusionResult(
        final_plate=final_text if status != "UNREADABLE" else None,
        confidence=round(confidence, 3),
        status=status,
        evidence_frame_ids=evidence_ids,
        num_observations=len(observations),
        validation=validation,
    )


if __name__ == "__main__":
    # Mirrors the worked example in the master prompt.
    obs = [
        Observation(101, "TN38A81234", ocr_confidence=0.55, quality_score=0.31),
        Observation(105, "TN38AB1234", ocr_confidence=0.88, quality_score=0.82),
        Observation(109, "TN38AB1234", ocr_confidence=0.93, quality_score=0.91),
        Observation(113, "TN38AB1234", ocr_confidence=0.90, quality_score=0.87),
        Observation(117, "TN38A81234", ocr_confidence=0.50, quality_score=0.29),
    ]
    result = fuse_observations(obs)
    print(result)
    assert result.final_plate == "TN38AB1234", "Self-test failed"
    print("Self-test passed: fusion correctly favored the high-quality observations.")
