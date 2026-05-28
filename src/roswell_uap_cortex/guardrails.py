"""Reasoning guardrails for local cognitive outputs."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ClaimMatrixStatus,
    ConfidenceBand,
    ContaminationFlagType,
    ReasoningContext,
    ReasoningOutput,
    ReasoningWarning,
    ReasoningWarningType,
    UncertaintyNote,
)


@dataclass(slots=True)
class ReasoningGuardrails:
    """Keep local reasoning bounded by provenance, lineage, and contradiction state."""

    def apply(self, context: ReasoningContext, output: ReasoningOutput) -> ReasoningOutput:
        self._add_warning(
            output,
            ReasoningWarningType.ASSOCIATION_NOT_CONFIRMATION,
            "Associations in context are retrieval hints, not confirmations.",
        )

        if context.activated_context.contested_associations or any(
            claim.status is ClaimMatrixStatus.CONTESTED for claim in context.claims
        ):
            output.confidence_band = ConfidenceBand.CONTESTED
            output.requires_review = True
            contested_ids = set(context.activated_context.activated_claim_ids)
            contested_ids.update(
                claim.id for claim in context.claims if claim.status is ClaimMatrixStatus.CONTESTED
            )
            output.contested_context_ids.update(contested_ids)
            self._add_warning(
                output,
                ReasoningWarningType.CONTRADICTION_VISIBLE,
                "Contested or contradictory context remains visible.",
                contested_ids,
            )

        unsupported_ids = {
            claim.id for claim in context.claims if claim.status is ClaimMatrixStatus.UNSUPPORTED
        }
        if unsupported_ids:
            output.requires_review = True
            self._add_warning(
                output,
                ReasoningWarningType.UNSUPPORTED_CLAIM,
                "Unsupported claims remain unsupported in reasoning output.",
                unsupported_ids,
            )

        provenance_evidence_ids = {record.evidence_id for record in context.provenance_records}
        missing_provenance = {
            item.id for item in context.evidence_items if item.id not in provenance_evidence_ids
        }
        if missing_provenance:
            output.requires_review = True
            output.confidence_band = self._lower_band(output.confidence_band)
            self._add_warning(
                output,
                ReasoningWarningType.MISSING_PROVENANCE,
                "Some evidence lacks provenance records.",
                missing_provenance,
            )

        lineage_counts: dict[str, int] = {}
        for record in context.lineage_records:
            lineage_counts[record.lineage_id] = lineage_counts.get(record.lineage_id, 0) + 1
        repeated_lineage_ids = {
            record.evidence_id
            for record in context.lineage_records
            if lineage_counts.get(record.lineage_id, 0) > 1
        }
        if repeated_lineage_ids:
            self._add_warning(
                output,
                ReasoningWarningType.SAME_LINEAGE_REPETITION,
                "Repeated same-lineage evidence is not independent corroboration.",
                repeated_lineage_ids,
            )

        fictional_ids = {
            item.id
            for item in context.evidence_items
            if ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS.value
            in set(item.metadata.get("contamination_flags", []))
        }
        if fictional_ids:
            output.requires_review = True
            self._add_warning(
                output,
                ReasoningWarningType.FICTIONAL_CONTAMINATION,
                "Fictional contamination terms were present in context.",
                fictional_ids,
            )

        for hypothesis in output.possible_hypotheses:
            hypothesis.speculative = True
        if output.possible_hypotheses:
            self._add_warning(
                output,
                ReasoningWarningType.SPECULATIVE_HYPOTHESIS,
                "Possible hypotheses are speculative and not confirmations.",
            )

        for note in context.uncertainty_notes:
            if note.note not in {existing.note for existing in output.uncertainty_notes}:
                output.uncertainty_notes.append(note)
        return output

    def _add_warning(
        self,
        output: ReasoningOutput,
        warning_type: ReasoningWarningType,
        message: str,
        related_ids: set[str] | None = None,
    ) -> None:
        if any(warning.warning_type is warning_type for warning in output.reasoning_warnings):
            return
        output.reasoning_warnings.append(
            ReasoningWarning(
                warning_type=warning_type,
                message=message,
                related_ids=related_ids or set(),
            )
        )

    def _lower_band(self, band: ConfidenceBand) -> ConfidenceBand:
        if band in {ConfidenceBand.HIGH_CONTEXT_SUPPORT, ConfidenceBand.MEDIUM}:
            return ConfidenceBand.LOW
        return band
