"""Deterministic mock reasoning harness for Phase 6 tests."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.llm_adapter import LocalLLMAdapter
from roswell_uap_cortex.models import (
    ClaimMatrixStatus,
    ConfidenceBand,
    ReasoningContext,
    ReasoningObservation,
    ReasoningOutput,
    UncertaintyNote,
)


@dataclass(slots=True)
class MockReasoner(LocalLLMAdapter):
    """Produce structured outputs from supplied context without hallucinated confirmation."""

    backend_name: str = "deterministic_mock_reasoner"

    def reason(self, context: ReasoningContext) -> ReasoningOutput:
        output = ReasoningOutput()

        for item in sorted(context.evidence_items, key=lambda evidence: evidence.id):
            output.observations.append(
                ReasoningObservation(
                    text=f"Evidence context: {item.summary}",
                    context_ids={item.id},
                    speculative=False,
                )
            )
            output.supporting_context_ids.add(item.id)

        for claim in sorted(context.claims, key=lambda claim_item: claim_item.id):
            if claim.status is ClaimMatrixStatus.CONTESTED:
                output.observations.append(
                    ReasoningObservation(
                        text=f"Contested claim remains unresolved: {claim.text}",
                        context_ids={claim.id},
                        speculative=False,
                    )
                )
                output.contested_context_ids.add(claim.id)
            elif claim.status is ClaimMatrixStatus.UNSUPPORTED:
                output.uncertainty_notes.append(
                    UncertaintyNote(
                        note=f"Unsupported claim remains unsupported: {claim.text}",
                        related_ids={claim.id},
                    )
                )
            output.supporting_context_ids.add(claim.id)

        for candidate in context.selected_candidates:
            if candidate.score.final_association_score < 0.5:
                output.uncertainty_notes.append(
                    UncertaintyNote(
                        note=f"Weak association retained for review: {candidate.label}",
                        related_ids={candidate.record_id},
                    )
                )

        if context.evidence_items or context.claims:
            output.possible_hypotheses.append(
                ReasoningObservation(
                    text="Speculative hypothesis: supplied context may be related, but association is not confirmation.",
                    context_ids=set(output.supporting_context_ids),
                    speculative=True,
                )
            )

        output.confidence_band = self._confidence_band(context)
        output.provenance_summary = self._provenance_summary(context)
        return output

    def _confidence_band(self, context: ReasoningContext) -> ConfidenceBand:
        if context.activated_context.contested_associations or any(
            claim.status is ClaimMatrixStatus.CONTESTED for claim in context.claims
        ):
            return ConfidenceBand.CONTESTED
        if not context.evidence_items and not context.claims:
            return ConfidenceBand.INSUFFICIENT_CONTEXT
        if len(context.provenance_records) < len(context.evidence_items):
            return ConfidenceBand.LOW
        if len(context.evidence_items) >= 2:
            return ConfidenceBand.MEDIUM
        return ConfidenceBand.LOW

    def _provenance_summary(self, context: ReasoningContext) -> str:
        if not context.evidence_items:
            return "No evidence provenance supplied."
        provenance_count = len(context.provenance_records)
        evidence_count = len(context.evidence_items)
        source_kinds = sorted({record.source_kind for record in context.provenance_records})
        kind_text = ", ".join(source_kinds) if source_kinds else "unknown"
        return f"{provenance_count}/{evidence_count} evidence items include provenance; source kinds: {kind_text}."
