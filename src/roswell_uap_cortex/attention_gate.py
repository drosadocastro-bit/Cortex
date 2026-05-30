"""Attention gate for downstream deterministic context selection."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.attention import AttentionEngine
from roswell_uap_cortex.models import (
    AttentionCandidate,
    AttentionDecision,
    AttentionFocus,
    AttentionPolicy,
)


@dataclass(slots=True)
class AttentionGate:
    """Rank or defer records without deleting or mutating them."""

    engine: AttentionEngine = field(default_factory=AttentionEngine)

    def apply(
        self,
        candidates: list[AttentionCandidate],
        focus: AttentionFocus | None = None,
        policy: AttentionPolicy | str | None = None,
        *,
        limit: int = 8,
    ) -> AttentionDecision:
        decision = self.engine.prioritize(candidates, focus, policy, limit=limit)
        preserved = [
            candidate
            for candidate in candidates
            if (candidate.contested or candidate.contradiction_pressure > 0)
            and candidate.record_id not in {selected.record_id for selected in decision.selected_records}
        ]
        if preserved:
            decision.selected_records.extend(preserved)
            decision.selected_for_review.extend(preserved)
            decision.deferred_records = [
                candidate
                for candidate in decision.deferred_records
                if candidate.record_id not in {item.record_id for item in preserved}
            ]
        return decision
