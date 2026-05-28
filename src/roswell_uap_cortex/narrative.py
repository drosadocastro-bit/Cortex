"""Deterministic narrative construction for investigative discourse."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import DiscourseResponse, InvestigativeNarrative


@dataclass(slots=True)
class NarrativeBuilder:
    """Build readable narrative while separating observation, interpretation, and speculation."""

    def build(self, response: DiscourseResponse) -> InvestigativeNarrative:
        observations = self._sentence("Observed evidence", response.observed_evidence.items)
        interpretations = self._sentence(
            "Possible associations for review",
            response.possible_associations.items + response.weak_associations.items,
        )
        speculation = self._sentence(
            "Speculative hypotheses",
            response.speculative_hypotheses.items,
        )
        uncertainty = self._sentence(
            "Uncertainty and missing information",
            response.uncertainty_summary.items + response.missing_information.items,
        )
        return InvestigativeNarrative(
            observations=observations,
            interpretations=interpretations,
            speculation=speculation,
            uncertainty=uncertainty,
        )

    def _sentence(self, prefix: str, items: list[str]) -> str:
        if not items:
            return f"{prefix}: none supplied."
        return f"{prefix}: " + " ".join(item for item in items)
