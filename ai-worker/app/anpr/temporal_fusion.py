"""
app/anpr/temporal_fusion.py
===========================
Phase G — Temporal Quality-Aware ANPR Fusion.

Architecture
------------
Each vehicle track accumulates a bounded circular buffer of plate
observations.  When the buffer is queried for a final decision, the
fusion engine runs three progressively more sophisticated strategies:

  A. Simple majority           – most-common normalized text wins
  B. Confidence-weighted       – sum OCR confidence per candidate
  C. Quality + OCR weighted    – OCR × quality × detector confidence
     followed by character-level per-position voting across same-length
     candidates using the same weights.

The character-level vote is the primary output.  Its confidence is then
modulated by Indian plate structural validation (via plate_validator).

Decision states
---------------
  CONFIRMED    – high weighted confidence + ≥2 corroborating observations
                 + valid Indian plate format
  PROBABLE     – medium evidence; worth displaying but not authoritative
  UNREADABLE   – insufficient or contradictory evidence; plate is NOT shown

The fused result retains full provenance: supporting frame IDs, per-
candidate scores, and the best-evidence frame so the system stays
auditable.

CPU cost
--------
Pure Python over a bounded list (≤12 items by default).  Negligible
relative to YOLO or OCR.

Usage (standalone)
------------------
    python -m app.anpr.temporal_fusion

Unit tests
----------
    python tests/test_temporal_fusion.py
"""

from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional

from app.validation.plate_validator import validate_plate, ValidationResult


# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------

# How many observations to keep per track.
MAX_OBSERVATIONS_PER_TRACK: int = 12

# Confidence thresholds (tune after ablation in MILESTONE 18/22).
CONFIRMED_THRESHOLD: float = 0.70
PROBABLE_THRESHOLD: float  = 0.42

# Configurable Fast Path Thresholds (Early Confirmation)
FAST_PATH_PLATE_CONF: float = 0.85
FAST_PATH_OCR_CONF: float   = 0.90
FAST_PATH_QUALITY: float    = 0.80

# Require at least this many observations before issuing CONFIRMED.
MIN_OBS_FOR_CONFIRMED: int = 2

# Minimum individual observation weight worth including in fusion.
MIN_OBS_WEIGHT: float = 0.05

# Max edit distance between two candidate strings to attempt character merging.
MAX_EDIT_DISTANCE_FOR_MERGE: int = 3


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ObservationRecord:
    """
    One plate observation from a single frame.

    Provenance is preserved end-to-end so every fused result can be
    traced back to its source frames.
    """
    frame_id:             int
    track_id:             int
    raw_text:             str          # verbatim from OCR engine
    normalized_text:      str          # cleaned (see _normalize)
    ocr_confidence:       float        # [0, 1] from OCR engine
    detector_confidence:  float        # [0, 1] from plate YOLO
    quality_score:        float        # [0, 1] from quality_scorer
    timestamp:            float        # time.perf_counter() or wall time

    @property
    def weight(self) -> float:
        """Composite trustworthiness of this single observation."""
        return self.ocr_confidence * self.quality_score * self.detector_confidence


@dataclass
class CandidateScore:
    """Accumulated evidence for one candidate plate string."""
    text:               str
    total_weight:       float = 0.0
    supporting_frames:  list[int] = field(default_factory=list)
    count:              int   = 0


@dataclass
class FusionResult:
    """
    Output of the fusion engine for one vehicle track.

    Fields
    ------
    fused_text            – final plate string, or None if UNREADABLE
    confidence            – [0, 1]; aggregate evidence strength
    decision              – "CONFIRMED" | "PROBABLE" | "UNREADABLE"
    supporting_frame_ids  – all frame IDs that contributed to this result
    supporting_obs_count  – number of individual observations used
    best_evidence_frame   – frame_id with highest individual weight
    candidate_scores      – ranked list of (text, weight, frame_count)
    validation            – ValidationResult from plate_validator (may be None)
    strategy_scores       – dict {"majority": …, "conf_weighted": …,
                                  "quality_weighted": …, "char_vote": …}
    """
    fused_text:           Optional[str]
    confidence:           float
    decision:             str
    supporting_frame_ids: list[int]
    supporting_obs_count: int
    best_evidence_frame:  Optional[int]
    candidate_scores:     list[CandidateScore]
    validation:           Optional[ValidationResult]
    strategy_scores:      dict
    count_agreement:      float = 0.0
    weighted_agreement:   float = 0.0
    dominant_text:        str = ""
    unique_texts:         int = 0
    is_fast_path:         bool = False


# ---------------------------------------------------------------------------
# Telemetry accumulator (module-level singleton, reset-able)
# ---------------------------------------------------------------------------

@dataclass
class FusionTelemetry:
    total_observations_processed:    int   = 0
    fusion_attempts:                 int   = 0
    confirmed_count:                 int   = 0
    probable_count:                  int   = 0
    unreadable_count:                int   = 0
    total_quality_score:             float = 0.0
    total_fusion_confidence:         float = 0.0
    _quality_samples:                int   = 0
    _confidence_samples:             int   = 0
    _track_obs_counts:               dict[int, int] = field(default_factory=dict)
    
    current_buffer_size:             int   = 0
    average_current_buffer_size:     float = 0.0

    @property
    def average_quality_score(self) -> float:
        return self.total_quality_score / max(1, self._quality_samples)

    @property
    def average_fusion_confidence(self) -> float:
        return self.total_fusion_confidence / max(1, self._confidence_samples)

    def record_observation(self, track_id: int) -> None:
        self.total_observations_processed += 1
        self._track_obs_counts[track_id] = self._track_obs_counts.get(track_id, 0) + 1

    @property
    def max_observations_seen_for_any_track(self) -> int:
        return max(self._track_obs_counts.values()) if self._track_obs_counts else 0

    @property
    def tracks_with_1_observation(self) -> int:
        return sum(1 for v in self._track_obs_counts.values() if v == 1)

    @property
    def tracks_with_2plus_observations(self) -> int:
        return sum(1 for v in self._track_obs_counts.values() if v >= 2)

    def record_result(self, result: FusionResult) -> None:
        self.fusion_attempts += 1
        if result.decision == "CONFIRMED":
            self.confirmed_count += 1
        elif result.decision == "PROBABLE":
            self.probable_count += 1
        else:
            self.unreadable_count += 1
        self.total_fusion_confidence += result.confidence
        self._confidence_samples += 1

    def record_quality(self, q: float) -> None:
        self.total_quality_score += q
        self._quality_samples += 1


_telemetry = FusionTelemetry()


def get_telemetry() -> FusionTelemetry:
    return _telemetry


def reset_telemetry() -> None:
    global _telemetry
    _telemetry = FusionTelemetry()


# ---------------------------------------------------------------------------
# Per-track observation buffer
# ---------------------------------------------------------------------------

class TrackObservationBuffer:
    """
    Bounded circular buffer of ObservationRecord for a single vehicle track.

    Older observations are automatically evicted when the buffer is full
    (FIFO / oldest-first eviction).
    """

    def __init__(self, max_size: int = MAX_OBSERVATIONS_PER_TRACK) -> None:
        self._buf: deque[ObservationRecord] = deque(maxlen=max_size)

    def add(self, obs: ObservationRecord) -> None:
        _telemetry.record_quality(obs.quality_score)
        _telemetry.record_observation(obs.track_id)
        self._buf.append(obs)

    def observations(self) -> list[ObservationRecord]:
        return list(self._buf)

    def __len__(self) -> int:
        return len(self._buf)

    def best(self) -> Optional[ObservationRecord]:
        """Return the single observation with the highest composite weight."""
        if not self._buf:
            return None
        return max(self._buf, key=lambda o: o.weight)


class MultiTrackBuffer:
    """
    Registry of per-track buffers across all active vehicle tracks.

    Call `prune(active_ids)` each frame to release memory for tracks
    that ByteTrack has evicted.
    """

    def __init__(self, max_per_track: int = MAX_OBSERVATIONS_PER_TRACK) -> None:
        self._max = max_per_track
        self._tracks: dict[int, TrackObservationBuffer] = {}

    def add(self, obs: ObservationRecord) -> None:
        if obs.track_id not in self._tracks:
            self._tracks[obs.track_id] = TrackObservationBuffer(self._max)
        self._tracks[obs.track_id].add(obs)

    def get(self, track_id: int) -> list[ObservationRecord]:
        buf = self._tracks.get(track_id)
        return buf.observations() if buf else []

    def best_for_track(self, track_id: int) -> Optional[ObservationRecord]:
        buf = self._tracks.get(track_id)
        return buf.best() if buf else None

    def prune(self, active_track_ids: set[int]) -> None:
        """Remove buffers for tracks no longer active in the tracker."""
        stale = [tid for tid in self._tracks if tid not in active_track_ids]
        for tid in stale:
            del self._tracks[tid]

    def active_track_ids(self) -> list[int]:
        return list(self._tracks.keys())

    def update_buffer_telemetry(self) -> None:
        if not self._tracks:
            _telemetry.current_buffer_size = 0
            _telemetry.average_current_buffer_size = 0.0
            return
        total = sum(len(b) for b in self._tracks.values())
        _telemetry.current_buffer_size = total
        _telemetry.average_current_buffer_size = total / len(self._tracks)

    def observation_counts(self) -> dict[int, int]:
        return {tid: len(buf) for tid, buf in self._tracks.items()}


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

def normalize_plate_text(raw: str) -> str:
    """
    Conservative normalization for Indian plate OCR output.

    Rules:
    - Uppercase everything
    - Strip leading/trailing whitespace
    - Collapse internal whitespace and common separators (-, ·)
    - Remove anything that is neither A-Z nor 0-9

    Deliberately does NOT perform O↔0, I↔1, B↔8, S↔5 substitutions —
    those are handled only inside the validator under controlled conditions.
    """
    text = raw.upper().strip()
    # Remove hyphens, dots, and spaces (common OCR artefacts from plate separators)
    text = re.sub(r"[\s\-·]+", "", text)
    # Keep only alphanumeric
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


# ---------------------------------------------------------------------------
# Edit distance (Levenshtein) — pure Python, small strings only
# ---------------------------------------------------------------------------

def _edit_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            )
        prev = curr
    return prev[len(b)]


# ---------------------------------------------------------------------------
# Fusion strategies
# ---------------------------------------------------------------------------

def _strategy_majority(observations: list[ObservationRecord]) -> tuple[str, float]:
    """A: Simple majority — most-frequently-seen normalized text wins."""
    counts: dict[str, int] = defaultdict(int)
    for obs in observations:
        if obs.normalized_text:
            counts[obs.normalized_text] += 1
    if not counts:
        return "", 0.0
    winner = max(counts, key=counts.__getitem__)
    confidence = counts[winner] / len(observations)
    return winner, confidence


def _strategy_conf_weighted(observations: list[ObservationRecord]) -> tuple[str, float]:
    """B: Confidence-weighted — sum OCR confidence per candidate."""
    scores: dict[str, float] = defaultdict(float)
    total = 0.0
    for obs in observations:
        if obs.normalized_text:
            scores[obs.normalized_text] += obs.ocr_confidence
            total += obs.ocr_confidence
    if not scores or total == 0:
        return "", 0.0
    winner = max(scores, key=scores.__getitem__)
    return winner, scores[winner] / total


def _strategy_quality_weighted(observations: list[ObservationRecord]) -> tuple[str, float]:
    """C: Quality+OCR+Detector weighted — composite score per candidate."""
    scores: dict[str, float] = defaultdict(float)
    total = 0.0
    for obs in observations:
        if obs.normalized_text and obs.weight >= MIN_OBS_WEIGHT:
            scores[obs.normalized_text] += obs.weight
            total += obs.weight
    if not scores or total == 0:
        return "", 0.0
    winner = max(scores, key=scores.__getitem__)
    return winner, scores[winner] / total


def _strategy_char_vote(
    observations: list[ObservationRecord],
) -> tuple[str, float]:
    """
    D: Character-position weighted voting.

    1. Find the modal length (weighted by observation weight).
    2. For same-length observations, vote per position using composite weight.
    3. The winner at each position is the char with most accumulated weight.
    4. Mean position-agreement across all positions = confidence proxy.
    """
    if not observations:
        return "", 0.0

    usable = [o for o in observations if o.normalized_text and o.weight >= MIN_OBS_WEIGHT]
    if not usable:
        return "", 0.0

    # Weighted modal length
    len_weights: dict[int, float] = defaultdict(float)
    for obs in usable:
        len_weights[len(obs.normalized_text)] += obs.weight
    modal_len = max(len_weights, key=len_weights.__getitem__)

    # Restrict to same-length candidates
    same_len = [o for o in usable if len(o.normalized_text) == modal_len]
    if not same_len:
        best = max(usable, key=lambda o: o.weight)
        return best.normalized_text, best.weight

    # Per-position vote
    voted_chars: list[str] = []
    position_agreements: list[float] = []

    for pos in range(modal_len):
        pos_votes: dict[str, float] = defaultdict(float)
        for obs in same_len:
            pos_votes[obs.normalized_text[pos]] += obs.weight
        total_pos = sum(pos_votes.values())
        winner_ch = max(pos_votes, key=pos_votes.__getitem__)
        agreement = pos_votes[winner_ch] / total_pos if total_pos > 0 else 0.0
        voted_chars.append(winner_ch)
        position_agreements.append(agreement)

    voted_str = "".join(voted_chars)
    mean_agreement = sum(position_agreements) / len(position_agreements)
    return voted_str, mean_agreement


# ---------------------------------------------------------------------------
# Candidate ranking (for provenance)
# ---------------------------------------------------------------------------

def _rank_candidates(observations: list[ObservationRecord]) -> list[CandidateScore]:
    """Return quality-weighted candidate list, sorted descending by score."""
    accum: dict[str, CandidateScore] = {}
    for obs in observations:
        txt = obs.normalized_text
        if not txt:
            continue
        if txt not in accum:
            accum[txt] = CandidateScore(text=txt)
        accum[txt].total_weight += obs.weight
        accum[txt].supporting_frames.append(obs.frame_id)
        accum[txt].count += 1
    ranked = sorted(accum.values(), key=lambda c: c.total_weight, reverse=True)
    return ranked


# ---------------------------------------------------------------------------
# Main fusion entry point
# ---------------------------------------------------------------------------

def fuse_observations(
    observations: list[ObservationRecord],
    *,
    track_id: Optional[int] = None,
) -> FusionResult:
    """
    Fuse a list of plate observations for a single vehicle track.

    This function is independently testable: it only depends on the
    list of ObservationRecord objects passed in.

    Parameters
    ----------
    observations : list[ObservationRecord]
        The full bounded history for a track (order is oldest-first).
    track_id : int, optional
        Used only for logging/provenance; not required for computation.

    Returns
    -------
    FusionResult
    """
    _null = FusionResult(
        fused_text=None,
        confidence=0.0,
        decision="UNREADABLE",
        supporting_frame_ids=[],
        supporting_obs_count=0,
        best_evidence_frame=None,
        candidate_scores=[],
        validation=None,
        strategy_scores={},
    )

    if not observations:
        _telemetry.record_result(_null)
        return _null

    # Filter out blank / whitespace-only observations
    valid_obs = [o for o in observations if o.normalized_text]
    if not valid_obs:
        _telemetry.record_result(_null)
        return _null

    # Run all four strategies
    maj_text,  maj_conf  = _strategy_majority(valid_obs)
    cwt_text,  cwt_conf  = _strategy_conf_weighted(valid_obs)
    qwt_text,  qwt_conf  = _strategy_quality_weighted(valid_obs)
    cvt_text,  cvt_conf  = _strategy_char_vote(valid_obs)

    strategy_scores = {
        "majority":        {"text": maj_text,  "confidence": round(maj_conf,  3)},
        "conf_weighted":   {"text": cwt_text,  "confidence": round(cwt_conf,  3)},
        "quality_weighted":{"text": qwt_text,  "confidence": round(qwt_conf,  3)},
        "char_vote":       {"text": cvt_text,  "confidence": round(cvt_conf,  3)},
    }

    # Primary decision is char_vote; fall back gracefully
    primary_text = cvt_text or qwt_text or cwt_text or maj_text
    primary_conf = cvt_conf  # char_vote agreement is the best confidence proxy

    if not primary_text:
        _telemetry.record_result(_null)
        return _null

    # Provenance
    candidate_scores = _rank_candidates(valid_obs)
    support_frames   = [o.frame_id for o in valid_obs]
    best_obs         = max(valid_obs, key=lambda o: o.weight)
    best_frame       = best_obs.frame_id

    # Indian plate validation — modulates confidence, never forces characters
    validation = validate_plate(primary_text)

    # Blend: 60% char-vote agreement, 30% mean observation weight, 10% n_obs bonus
    mean_weight = sum(o.weight for o in valid_obs) / len(valid_obs)
    n_obs_bonus = min(len(valid_obs) / 5.0, 1.0) * 0.10   # +0.10 max at 5+ obs
    raw_conf = 0.60 * primary_conf + 0.30 * mean_weight + n_obs_bonus

    # Validation modulation
    if validation and validation.is_valid:
        final_text = validation.corrected_text    # may include safe single-char repair
        confidence = min(raw_conf + 0.10, 1.0)
    else:
        final_text = primary_text
        confidence = max(raw_conf - 0.15, 0.0)

    confidence = round(confidence, 3)

    # Calculate Agreements
    dominant_text = ""
    count_agreement = 0.0
    weighted_agreement = 0.0
    unique_texts = 0
    if candidate_scores:
        best_cand = candidate_scores[0]
        dominant_text = best_cand.text
        unique_texts = len(candidate_scores)
        count_agreement = best_cand.count / len(valid_obs)
        total_w = sum(c.total_weight for c in candidate_scores)
        weighted_agreement = best_cand.total_weight / max(1e-6, total_w)
    
    # -------------------------------------------------------------
    # 8. TRUE EARLY-CONFIRMATION FAST PATH
    # -------------------------------------------------------------
    is_fast_path = False
    
    # Fast path triggered if there is an EXCELLENT single observation and no contradictory history
    # "No contradictory history" -> high weighted_agreement across the track
    if best_obs and validation and validation.is_valid:
        if (best_obs.detector_confidence > FAST_PATH_PLATE_CONF and
            best_obs.ocr_confidence > FAST_PATH_OCR_CONF and
            best_obs.quality_score > FAST_PATH_QUALITY):
            # Check if there is no strong contradictory history (agreement > 0.7 or few observations)
            if weighted_agreement > 0.70 or len(valid_obs) <= 1:
                is_fast_path = True
    
    # Decision
    if is_fast_path:
        decision = "CONFIRMED"
        confidence = max(confidence, 0.95)
    elif (
        confidence >= CONFIRMED_THRESHOLD
        and len(valid_obs) >= MIN_OBS_FOR_CONFIRMED
        and validation
        and validation.is_valid
    ):
        decision = "CONFIRMED"
    elif confidence >= PROBABLE_THRESHOLD:
        decision = "PROBABLE"
    else:
        decision = "UNREADABLE"

    result = FusionResult(
        fused_text=final_text if decision != "UNREADABLE" else None,
        confidence=confidence,
        decision=decision,
        supporting_frame_ids=support_frames,
        supporting_obs_count=len(valid_obs),
        best_evidence_frame=best_frame,
        candidate_scores=candidate_scores,
        validation=validation,
        strategy_scores=strategy_scores,
        count_agreement=count_agreement,
        weighted_agreement=weighted_agreement,
        dominant_text=dominant_text,
        unique_texts=unique_texts,
        is_fast_path=is_fast_path
    )

    _telemetry.record_result(result)
    return result


# ---------------------------------------------------------------------------
# Ablation methods (A–E) — callable with the same observations list
# ---------------------------------------------------------------------------

def ablation_a_single_frame(observations: list[ObservationRecord]) -> FusionResult:
    """A: Use only the single most recent observation."""
    if not observations:
        return fuse_observations([])
    return fuse_observations([observations[-1]])


def ablation_b_best_frame(observations: list[ObservationRecord]) -> FusionResult:
    """B: Use only the single highest-quality observation."""
    if not observations:
        return fuse_observations([])
    best = max(observations, key=lambda o: o.weight)
    return fuse_observations([best])


def ablation_c_multi_frame(observations: list[ObservationRecord]) -> FusionResult:
    """C: Multi-frame majority only (no quality weighting)."""
    if not observations:
        return fuse_observations([])
    # Reuse fuse_observations but with equal weights
    flat_obs = [
        ObservationRecord(
            frame_id=o.frame_id,
            track_id=o.track_id,
            raw_text=o.raw_text,
            normalized_text=o.normalized_text,
            ocr_confidence=o.ocr_confidence,
            detector_confidence=1.0,   # neutralise
            quality_score=1.0,         # neutralise
            timestamp=o.timestamp,
        )
        for o in observations
    ]
    return fuse_observations(flat_obs)


def ablation_d_quality_weighted(observations: list[ObservationRecord]) -> FusionResult:
    """D: Multi-frame + quality weighting (full char_vote, no validation)."""
    return fuse_observations(observations)   # standard pipeline, validation applied below


def ablation_e_full_pipeline(observations: list[ObservationRecord]) -> FusionResult:
    """E: Full pipeline including Indian plate validation."""
    return fuse_observations(observations)


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def make_observation(
    frame_id: int,
    track_id: int,
    raw_text: str,
    ocr_confidence: float,
    quality_score: float,
    detector_confidence: float = 1.0,
    timestamp: Optional[float] = None,
) -> ObservationRecord:
    """Helper for tests and the realtime loop."""
    return ObservationRecord(
        frame_id=frame_id,
        track_id=track_id,
        raw_text=raw_text,
        normalized_text=normalize_plate_text(raw_text),
        ocr_confidence=ocr_confidence,
        quality_score=quality_score,
        detector_confidence=detector_confidence,
        timestamp=timestamp if timestamp is not None else time.perf_counter(),
    )


# ---------------------------------------------------------------------------
# Self-test / demo (python -m app.anpr.temporal_fusion)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Temporal Fusion Self-Test")
    print("=" * 60)

    obs = [
        make_observation(101, 7, "TN38A81234",  0.55, 0.31),
        make_observation(105, 7, "TN38AB1234",  0.88, 0.82),
        make_observation(109, 7, "TN38AB1234",  0.93, 0.91),
        make_observation(113, 7, "TN38AB1234",  0.90, 0.87),
        make_observation(117, 7, "TN38A81234",  0.50, 0.29),
    ]

    result = fuse_observations(obs)
    print(f"Decision     : {result.decision}")
    print(f"Fused text   : {result.fused_text}")
    print(f"Confidence   : {result.confidence}")
    print(f"Observations : {result.supporting_obs_count}")
    print(f"Best frame   : {result.best_evidence_frame}")
    print(f"Validation   : {result.validation}")
    print(f"Strategies   : {result.strategy_scores}")
    print()

    assert result.fused_text == "TN38AB1234", f"Expected TN38AB1234, got {result.fused_text}"
    assert result.decision in ("CONFIRMED", "PROBABLE"), f"Expected CONFIRMED/PROBABLE, got {result.decision}"
    print("Self-test PASSED.")
