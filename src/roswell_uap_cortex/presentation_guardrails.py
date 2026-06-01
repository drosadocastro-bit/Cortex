"""Guardrails for read-only workflow presentation models."""

from __future__ import annotations

from dataclasses import dataclass
import re

from roswell_uap_cortex.models import PresentationWarning, ReviewDashboardView


@dataclass(slots=True)
class PresentationGuardrails:
    """Keep presentation output from becoming conclusions or truth state."""

    certainty_terms: tuple[str, ...] = (
        "confirmed",
        "proven",
        "debunked",
        "validated",
        "verified true",
        "definitive",
        "rejected source",
    )

    def check(self, dashboard: ReviewDashboardView) -> list[PresentationWarning]:
        warnings: list[PresentationWarning] = []
        text = self._flatten(dashboard).casefold()
        for term in self.certainty_terms:
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text):
                warnings.append(
                    PresentationWarning(
                        "certainty_language",
                        f"Presentation contains certainty-inflating term: {term}",
                    )
                )

        if not dashboard.synthetic_only:
            warnings.append(PresentationWarning("missing_synthetic_label", "Presentation must preserve synthetic/demo labeling."))
        if not dashboard.limitations and not (dashboard.bundle_preview and dashboard.bundle_preview.limitations):
            warnings.append(PresentationWarning("missing_limitations", "Presentation must preserve review limitations."))
        if not dashboard.provenance_refs:
            warnings.append(PresentationWarning("missing_provenance", "Presentation should expose provenance references."))
        if dashboard.contradiction_ids and "contradiction" not in text:
            warnings.append(PresentationWarning("hidden_contradiction", "Presentation must keep contradictions visible."))

        warnings.append(
            PresentationWarning(
                "display_not_truth",
                "Presentation view models are display state only; priority is not truth confidence.",
            )
        )
        return self._merge(warnings)

    def apply(self, dashboard: ReviewDashboardView) -> ReviewDashboardView:
        dashboard.warnings = self._merge(dashboard.warnings + self.check(dashboard))
        return dashboard

    def _flatten(self, dashboard: ReviewDashboardView) -> str:
        parts = [dashboard.title, *dashboard.uncertainty_notes, *dashboard.limitations]
        parts.extend(f"{stage.title} {stage.summary}" for stage in dashboard.stages)
        parts.extend(
            f"{card.claim_id} {card.canonical_topic} {card.text} {card.priority} {' '.join(card.notes)}"
            for card in dashboard.claim_cards
        )
        parts.extend(
            f"{card.source_id} {card.priority} {' '.join(card.notes)} {' '.join(sorted(card.contamination_flags))}"
            for card in dashboard.source_cards
        )
        if dashboard.session_timeline:
            parts.extend(dashboard.session_timeline.events)
        if dashboard.bundle_preview:
            parts.extend(dashboard.bundle_preview.section_titles)
            parts.extend(dashboard.bundle_preview.limitations)
        parts.extend(warning.message for warning in dashboard.warnings)
        return " ".join(parts)

    def _merge(self, warnings: list[PresentationWarning]) -> list[PresentationWarning]:
        by_key = {
            (warning.warning_type, warning.message, tuple(sorted(warning.related_ids))): warning
            for warning in warnings
        }
        return [by_key[key] for key in sorted(by_key)]
