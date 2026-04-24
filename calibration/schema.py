# calibration/schema.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
schema.py — shared types for calibration-audit modules.

Stdlib-only. Provides a banded score enum, a per-dimension score
record, and a top-level CalibrationReport that aggregates them and
serializes to JSON.

Band convention (applies to the dimensions as written in
architecture_mismatch.py):

    GREEN   low score   — no concern on this dimension
    YELLOW  mid score   — some concern; watch
    RED     high score  — clear concern; apply correction
    EXTINCT very high   — correction is overdue; substrate is
                          already compromised
"""

from __future__ import annotations

import enum
import json
from dataclasses import dataclass, field
from typing import Any


class Band(str, enum.Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    EXTINCT = "EXTINCT"

    # Thresholds on [0.0, 1.0]. A score >= THRESHOLD[band] lands in that
    # band. The scale treats higher scores as higher concern, so that
    # mismatch-risk / damage / cascade modules can reuse the same enum.
    _THRESHOLDS = {
        "YELLOW": 0.30,
        "RED":    0.60,
        "EXTINCT": 0.85,
    }

    @classmethod
    def from_score(cls, score: float) -> "Band":
        if score >= 0.85:
            return cls.EXTINCT
        if score >= 0.60:
            return cls.RED
        if score >= 0.30:
            return cls.YELLOW
        return cls.GREEN


@dataclass
class DimensionScore:
    """One dimension of a calibration audit.

    name       — stable identifier for the dimension
    score      — [0.0, 1.0]; higher = more concern on this dimension
    band       — Band derived from score
    evidence   — human-readable bullets supporting the score
    falsifier  — a statement that, if true, would invalidate this
                 dimension's score
    """
    name: str
    score: float
    band: Band
    evidence: list[str] = field(default_factory=list)
    falsifier: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": round(float(self.score), 4),
            "band": self.band.value,
            "evidence": list(self.evidence),
            "falsifier": self.falsifier,
        }


@dataclass
class CalibrationReport:
    """Aggregated output of a calibration audit."""
    module: str
    system_id: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    aggregate_score: float = 0.0
    aggregate_band: Band = Band.GREEN
    verdict: str = ""
    failing_dimensions: list[str] = field(default_factory=list)
    falsifiable_claims: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def aggregate(cls, scores: list[float]) -> tuple[float, Band]:
        """Mean of per-dimension scores, mapped to a Band."""
        if not scores:
            return 0.0, Band.GREEN
        avg = sum(scores) / len(scores)
        return avg, Band.from_score(avg)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "system_id": self.system_id,
            "aggregate_score": round(float(self.aggregate_score), 4),
            "aggregate_band": self.aggregate_band.value,
            "verdict": self.verdict,
            "failing_dimensions": list(self.failing_dimensions),
            "falsifiable_claims": list(self.falsifiable_claims),
            "dimensions": [d.to_dict() for d in self.dimensions],
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
