"""Structured investigative discourse from activated context and reasoning output."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.citations import CitationFormatter
from roswell_uap_cortex.discourse_guardrails import DiscourseGuardrails
from roswell_uap_cortex.models import (
    ActivatedContext,
    DiscourseRequest,
    DiscourseResponse,
    DiscourseSection,
    EvidenceItem,
    ProvenanceRecord,
    ReasoningOutput,
    SourceLineageRecord,
)
from roswell_uap_cortex.narrative import NarrativeBuilder
from roswell_uap_cortex.uncertainty import UncertaintyFormatter


@dataclass(slots=True)
class DiscourseEngine:
    """Produce bounded human-review discourse without confirming associations."""

    citation_formatter: CitationFormatter = field(default_factory=CitationFormatter)
    uncertainty_formatter: UncertaintyFormatter = field(default_factory=UncertaintyFormatter)
    narrative_builder: NarrativeBuilder = field(default_factory=NarrativeBuilder)
    guardrails: DiscourseGuardrails = field(default_factory=DiscourseGuardrails)

    def build(
        self,
        request: DiscourseRequest,
        *,
        evidence_by_id: dict[str, EvidenceItem] | None = None,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
        lineage_by_evidence_id: dict[str, SourceLineageRecord] | None = None,
    ) -> DiscourseResponse:
        evidence_by_id = evidence_by_id or {}
        provenance_by_evidence_id = provenance_by_evidence_id or {}
        lineage_by_evidence_id = lineage_by_evidence_id or {}
        reasoning = request.reasoning_output
        activated = request.activated_context

        citations = self._citations_for_reasoning(
            reasoning,
            evidence_by_id=evidence_by_id,
            provenance_by_evidence_id=provenance_by_evidence_id,
            lineage_by_evidence_id=lineage_by_evidence_id,
        )
        citations = self.citation_formatter.merge(citations)

        observed = DiscourseSection(
            title="Observed Evidence",
            items=[
                observation.text
                for observation in reasoning.observations
                if not observation.speculative
            ],
            citations=citations,
        )
        possible = DiscourseSection(
            title="Possible Associations",
            items=[
                f"Possible association: {candidate.label}"
                for candidate in sorted(
                    activated.contested_associations,
                    key=lambda item: item.record_id,
                )
            ],
        )
        contradictions = DiscourseSection(
            title="Contradictions",
            items=[
                f"Unresolved contradiction or contested context: {context_id}"
                for context_id in sorted(reasoning.contested_context_ids)
            ],
        )
        weak = DiscourseSection(
            title="Weak Associations",
            items=[
                f"Weak association retained for review: {candidate.label}"
                for candidate in sorted(activated.weak_associations, key=lambda item: item.record_id)
            ],
        )
        speculative = DiscourseSection(
            title="Speculative Hypotheses",
            items=[
                f"Speculative: {hypothesis.text}"
                for hypothesis in reasoning.possible_hypotheses
            ],
        )
        provenance_notes = DiscourseSection(
            title="Provenance Notes",
            items=[reasoning.provenance_summary] if reasoning.provenance_summary else [],
            citations=citations,
        )
        uncertainty = self.uncertainty_formatter.summarize(reasoning, activated)
        missing = DiscourseSection(
            title="Missing Information",
            items=self._missing_information(reasoning, citations),
        )

        response = DiscourseResponse(
            observed_evidence=observed,
            possible_associations=possible,
            contradictions=contradictions,
            weak_associations=weak,
            speculative_hypotheses=speculative,
            provenance_notes=provenance_notes,
            uncertainty_summary=uncertainty,
            missing_information=missing,
            reasoning_warnings=list(reasoning.reasoning_warnings),
            citations=citations,
            review_required=reasoning.requires_review,
        )
        response.narrative = self.narrative_builder.build(response)
        return self.guardrails.apply(response)

    def _citations_for_reasoning(
        self,
        reasoning: ReasoningOutput,
        *,
        evidence_by_id: dict[str, EvidenceItem],
        provenance_by_evidence_id: dict[str, ProvenanceRecord],
        lineage_by_evidence_id: dict[str, SourceLineageRecord],
    ):
        evidence_ids: set[str] = set(reasoning.supporting_context_ids)
        evidence_ids.update(reasoning.contested_context_ids)
        for observation in reasoning.observations:
            evidence_ids.update(observation.context_ids)
        for hypothesis in reasoning.possible_hypotheses:
            evidence_ids.update(hypothesis.context_ids)

        citations = []
        for evidence_id in sorted(evidence_ids):
            if evidence_id not in evidence_by_id and evidence_id not in provenance_by_evidence_id:
                continue
            citations.append(
                self.citation_formatter.citation_for(
                    evidence_id,
                    provenance=provenance_by_evidence_id.get(evidence_id),
                    lineage=lineage_by_evidence_id.get(evidence_id),
                    source_id=evidence_by_id[evidence_id].source_id
                    if evidence_id in evidence_by_id
                    else None,
                )
            )
        return citations

    def _missing_information(self, reasoning: ReasoningOutput, citations) -> list[str]:
        items: list[str] = []
        if not citations and (reasoning.observations or reasoning.possible_hypotheses):
            items.append("No provenance citations were available for some supplied context.")
        for warning in reasoning.reasoning_warnings:
            if "missing" in warning.warning_type.value:
                items.append(warning.message)
        return sorted(set(items))
