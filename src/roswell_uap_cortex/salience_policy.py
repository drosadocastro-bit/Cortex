"""Deterministic attention policy presets."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import AttentionPolicy, AttentionSignal


BASE_WEIGHTS = {
    AttentionSignal.RELEVANCE: 0.10,
    AttentionSignal.NOVELTY: 0.08,
    AttentionSignal.CONTRADICTION_PRESSURE: 0.14,
    AttentionSignal.PROVENANCE_FRAGILITY: 0.12,
    AttentionSignal.SOURCE_TRUST: 0.06,
    AttentionSignal.SOURCE_INDEPENDENCE: 0.08,
    AttentionSignal.TEMPORAL_IMPORTANCE: 0.08,
    AttentionSignal.CONTAMINATION_RISK: 0.10,
    AttentionSignal.RECURRENCE: 0.05,
    AttentionSignal.UNCERTAINTY_LOAD: 0.09,
    AttentionSignal.USER_FOCUS_MATCH: 0.10,
}


@dataclass(slots=True)
class SaliencePolicyEngine:
    """Provide deterministic salience weighting presets."""

    def policy(self, name: str = "conservative") -> AttentionPolicy:
        name = name.casefold().strip()
        weights = dict(BASE_WEIGHTS)
        if name == "exploratory":
            weights.update(
                {
                    AttentionSignal.NOVELTY: 0.16,
                    AttentionSignal.RELEVANCE: 0.14,
                    AttentionSignal.USER_FOCUS_MATCH: 0.16,
                    AttentionSignal.PROVENANCE_FRAGILITY: 0.08,
                    AttentionSignal.CONTAMINATION_RISK: 0.07,
                }
            )
        elif name == "contradiction_first":
            weights.update(
                {
                    AttentionSignal.CONTRADICTION_PRESSURE: 0.28,
                    AttentionSignal.UNCERTAINTY_LOAD: 0.14,
                    AttentionSignal.USER_FOCUS_MATCH: 0.08,
                }
            )
        elif name == "provenance_first":
            weights.update(
                {
                    AttentionSignal.PROVENANCE_FRAGILITY: 0.26,
                    AttentionSignal.SOURCE_INDEPENDENCE: 0.12,
                    AttentionSignal.SOURCE_TRUST: 0.10,
                    AttentionSignal.USER_FOCUS_MATCH: 0.08,
                }
            )
        elif name == "contamination_watch":
            weights.update(
                {
                    AttentionSignal.CONTAMINATION_RISK: 0.28,
                    AttentionSignal.PROVENANCE_FRAGILITY: 0.16,
                    AttentionSignal.CONTRADICTION_PRESSURE: 0.12,
                    AttentionSignal.USER_FOCUS_MATCH: 0.06,
                }
            )
        else:
            name = "conservative"
        return AttentionPolicy(name=name, weights=self._normalize(weights))

    def all_policies(self) -> dict[str, AttentionPolicy]:
        return {
            name: self.policy(name)
            for name in (
                "conservative",
                "exploratory",
                "contradiction_first",
                "provenance_first",
                "contamination_watch",
            )
        }

    def _normalize(self, weights: dict[AttentionSignal, float]) -> dict[AttentionSignal, float]:
        total = sum(max(0.0, value) for value in weights.values()) or 1.0
        return {signal: max(0.0, value) / total for signal, value in weights.items()}
