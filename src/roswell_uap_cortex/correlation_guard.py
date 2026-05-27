"""Guardrails that keep association from becoming confirmation."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import AssociationScore


@dataclass(slots=True)
class CorrelationGuard:
    """Apply deterministic caution rules to association scores."""

    low_independence_threshold: float = 0.35
    high_lexical_threshold: float = 0.45

    def apply(
        self,
        score: AssociationScore,
        *,
        lineage_id: str | None = None,
        contradiction_pressure: float = 0.0,
    ) -> tuple[AssociationScore, list[str]]:
        notes: list[str] = ["association is not confirmation"]

        if lineage_id is None:
            notes.append("unknown lineage; association should be treated cautiously")

        if score.lexical_overlap >= self.high_lexical_threshold and (
            score.source_independence <= self.low_independence_threshold
        ):
            score.final_association_score *= 0.65
            notes.append("high wording overlap with low source independence was downgraded")

        if contradiction_pressure > 0:
            penalty = _clamp(contradiction_pressure)
            score.contradiction_penalty = max(score.contradiction_penalty, penalty)
            score.final_association_score *= 1 - penalty * 0.55
            notes.append("contradiction pressure reduced association score")

        score.final_association_score = _clamp(score.final_association_score)
        return score, notes
