"""Uncertainty summaries for investigative discourse."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ActivatedContext,
    DiscourseSection,
    ReasoningOutput,
    ReasoningWarningType,
)


@dataclass(slots=True)
class UncertaintyFormatter:
    """Summarize unresolved uncertainty without resolving it."""

    def summarize(
        self,
        reasoning_output: ReasoningOutput,
        activated_context: ActivatedContext,
    ) -> DiscourseSection:
        items: list[str] = []
        warning_types = {warning.warning_type for warning in reasoning_output.reasoning_warnings}

        if activated_context.contested_associations or reasoning_output.contested_context_ids:
            items.append("Unresolved contradictions or contested associations remain visible.")
        if ReasoningWarningType.MISSING_PROVENANCE in warning_types:
            items.append("Some context has missing provenance.")
        if ReasoningWarningType.SAME_LINEAGE_REPETITION in warning_types:
            items.append("Repeated same-lineage evidence is not independent corroboration.")
        if reasoning_output.possible_hypotheses:
            items.append("Speculative hypotheses are present and remain labeled.")
        if not items:
            items.append("No additional uncertainty notes were produced by deterministic discourse.")

        for note in reasoning_output.uncertainty_notes:
            if note.note not in items:
                items.append(note.note)

        return DiscourseSection(title="Uncertainty Summary", items=items)
