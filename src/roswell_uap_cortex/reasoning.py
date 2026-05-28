"""Bounded local cognitive reasoning over activated context."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.context_builder import ContextWindowBuilder
from roswell_uap_cortex.guardrails import ReasoningGuardrails
from roswell_uap_cortex.llm_adapter import LocalLLMAdapter
from roswell_uap_cortex.mock_reasoner import MockReasoner
from roswell_uap_cortex.models import (
    ClaimNode,
    EvidenceItem,
    MemoryRecord,
    ProvenanceRecord,
    ReasoningOutput,
    ReasoningRequest,
    SourceLineageRecord,
)


@dataclass(slots=True)
class CognitiveReasoningEngine:
    """Run constrained reasoning without mutating evidence, graph, or claims."""

    context_builder: ContextWindowBuilder = field(default_factory=ContextWindowBuilder)
    adapter: LocalLLMAdapter = field(default_factory=MockReasoner)
    guardrails: ReasoningGuardrails = field(default_factory=ReasoningGuardrails)

    def reason(
        self,
        request: ReasoningRequest,
        *,
        evidence_by_id: dict[str, EvidenceItem] | None = None,
        claims_by_id: dict[str, ClaimNode] | None = None,
        memories_by_id: dict[str, MemoryRecord] | None = None,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
        lineage_by_evidence_id: dict[str, SourceLineageRecord] | None = None,
    ) -> ReasoningOutput:
        context = self.context_builder.build(
            request.activated_context,
            candidates=request.candidates,
            evidence_by_id=evidence_by_id,
            claims_by_id=claims_by_id,
            memories_by_id=memories_by_id,
            provenance_by_evidence_id=provenance_by_evidence_id,
            lineage_by_evidence_id=lineage_by_evidence_id,
            max_items=request.max_context_items,
        )
        output = self.adapter.reason(context)
        return self.guardrails.apply(context, output)
