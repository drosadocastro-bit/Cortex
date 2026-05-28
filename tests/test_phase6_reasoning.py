from copy import deepcopy

from roswell_uap_cortex import (
    ActivatedContext,
    AssociationCandidate,
    AssociationScore,
    ClaimMatrixStatus,
    ClaimNode,
    CognitiveReasoningEngine,
    ConfidenceBand,
    ContaminationFlagType,
    ContextWindowBuilder,
    EvidenceItem,
    GraphNode,
    GraphNodeType,
    ProvenanceRecord,
    ReasoningRequest,
    ReasoningWarningType,
    RelationshipGraphEngine,
    SourceLineageRecord,
)
from roswell_uap_cortex.mock_reasoner import MockReasoner


def evidence(
    evidence_id: str,
    summary: str,
    *,
    lineage_id: str = "line-a",
    flags: list[str] | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        id=evidence_id,
        summary=summary,
        source_id=f"source:{lineage_id}",
        evidence_type="note",
        metadata={
            "lineage_id": lineage_id,
            "contamination_flags": flags or [],
        },
    )


def provenance(item: EvidenceItem) -> ProvenanceRecord:
    return ProvenanceRecord(
        evidence_id=item.id,
        source_uri=item.source_id,
        source_kind="synthetic_note",
        ingestion_method="test",
        extraction_method="test",
        original_input_id=f"input:{item.id}",
    )


def lineage(item: EvidenceItem) -> SourceLineageRecord:
    return SourceLineageRecord(
        evidence_id=item.id,
        source_id=item.source_id,
        lineage_id=item.metadata["lineage_id"],
        source_uri=item.source_id,
    )


def candidate(
    record_id: str,
    *,
    evidence_ids: set[str],
    score: float = 0.8,
    record_type: str = "evidence",
) -> AssociationCandidate:
    return AssociationCandidate(
        record_id=record_id,
        record_type=record_type,
        label=f"candidate {record_id}",
        score=AssociationScore(final_association_score=score),
        evidence_ids=evidence_ids,
    )


def test_reasoning_preserves_contradictions() -> None:
    item = evidence("e1", "Context evidence")
    claim = ClaimNode(
        id="claim-1",
        text="event timing is contested",
        canonical_topic="timing",
        status=ClaimMatrixStatus.CONTESTED,
        evidence_ids={"e1"},
    )
    activated = ActivatedContext(
        activated_claim_ids={"claim-1"},
        activated_evidence_ids={"e1"},
        contested_associations=[
            candidate("claim-1", evidence_ids={"e1"}, record_type="claim")
        ],
    )

    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(query="timing", activated_context=activated),
        evidence_by_id={"e1": item},
        claims_by_id={"claim-1": claim},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    assert output.confidence_band is ConfidenceBand.CONTESTED
    assert "claim-1" in output.contested_context_ids
    assert ReasoningWarningType.CONTRADICTION_VISIBLE in {
        warning.warning_type for warning in output.reasoning_warnings
    }


def test_unsupported_claims_remain_unsupported() -> None:
    claim = ClaimNode(
        id="claim-u",
        text="unsupported assertion",
        canonical_topic="unsupported",
        status=ClaimMatrixStatus.UNSUPPORTED,
    )
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(
            query="unsupported",
            activated_context=ActivatedContext(activated_claim_ids={"claim-u"}),
        ),
        claims_by_id={"claim-u": claim},
    )

    assert ReasoningWarningType.UNSUPPORTED_CLAIM in {
        warning.warning_type for warning in output.reasoning_warnings
    }


def test_speculative_hypotheses_are_labeled_speculative() -> None:
    item = evidence("e1", "Possible related context")
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(
            query="possible",
            activated_context=ActivatedContext(activated_evidence_ids={"e1"}),
        ),
        evidence_by_id={"e1": item},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    assert output.possible_hypotheses
    assert all(hypothesis.speculative for hypothesis in output.possible_hypotheses)
    assert ReasoningWarningType.SPECULATIVE_HYPOTHESIS in {
        warning.warning_type for warning in output.reasoning_warnings
    }


def test_context_builder_reduces_duplicate_lineage_flooding() -> None:
    items = [evidence(f"e{i}", f"duplicate {i}", lineage_id="same") for i in range(4)]
    activated = ActivatedContext(activated_evidence_ids={item.id for item in items})
    context = ContextWindowBuilder(max_items=8, max_per_lineage=1).build(
        activated,
        evidence_by_id={item.id: item for item in items},
        provenance_by_evidence_id={item.id: provenance(item) for item in items},
        lineage_by_evidence_id={item.id: lineage(item) for item in items},
    )

    assert len(context.evidence_items) == 1
    assert any("trimmed" in note.note for note in context.uncertainty_notes)


def test_reasoning_output_contains_provenance_summary() -> None:
    item = evidence("e1", "Context evidence")
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(query="context", activated_context=ActivatedContext(activated_evidence_ids={"e1"})),
        evidence_by_id={"e1": item},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    assert "1/1 evidence items include provenance" in output.provenance_summary


def test_contamination_flags_produce_warnings() -> None:
    item = evidence(
        "e1",
        "Contaminated context",
        flags=[ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS.value],
    )
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(query="context", activated_context=ActivatedContext(activated_evidence_ids={"e1"})),
        evidence_by_id={"e1": item},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    assert ReasoningWarningType.FICTIONAL_CONTAMINATION in {
        warning.warning_type for warning in output.reasoning_warnings
    }


def test_reasoning_never_creates_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.EVIDENCE, label="evidence", id="e1"))

    CognitiveReasoningEngine().reason(
        ReasoningRequest(query="x", activated_context=ActivatedContext(activated_evidence_ids={"e1"})),
        evidence_by_id={"e1": evidence("e1", "Context evidence")},
    )

    assert graph.edges == {}


def test_reasoning_never_mutates_evidence_records() -> None:
    item = evidence("e1", "Immutable context")
    before = deepcopy(item)

    CognitiveReasoningEngine().reason(
        ReasoningRequest(query="immutable", activated_context=ActivatedContext(activated_evidence_ids={"e1"})),
        evidence_by_id={"e1": item},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    assert item == before


def test_confidence_band_remains_bounded() -> None:
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(query="empty", activated_context=ActivatedContext())
    )

    assert output.confidence_band in set(ConfidenceBand)


def test_mock_reasoning_remains_deterministic() -> None:
    item = evidence("e1", "Deterministic context")
    activated = ActivatedContext(activated_evidence_ids={"e1"})
    context = ContextWindowBuilder().build(
        activated,
        evidence_by_id={"e1": item},
        provenance_by_evidence_id={"e1": provenance(item)},
        lineage_by_evidence_id={"e1": lineage(item)},
    )

    first = MockReasoner().reason(context)
    second = MockReasoner().reason(context)

    assert first == second


def test_low_value_duplicate_context_is_trimmed() -> None:
    items = [
        evidence("e1", "first", lineage_id="line-a"),
        evidence("e2", "second", lineage_id="line-a"),
        evidence("e3", "third", lineage_id="line-b"),
    ]
    context = ContextWindowBuilder(max_items=3, max_per_lineage=1).build(
        ActivatedContext(activated_evidence_ids={item.id for item in items}),
        evidence_by_id={item.id: item for item in items},
        lineage_by_evidence_id={item.id: lineage(item) for item in items},
    )

    assert {record.metadata["lineage_id"] for record in context.evidence_items} == {
        "line-a",
        "line-b",
    }
    assert len(context.evidence_items) == 2


def test_focused_context_is_smaller_than_total_available_context() -> None:
    items = [evidence(f"e{i}", f"context {i}", lineage_id=f"line-{i}") for i in range(6)]
    context = ContextWindowBuilder(max_items=3).build(
        ActivatedContext(activated_evidence_ids={item.id for item in items}),
        evidence_by_id={item.id: item for item in items},
        lineage_by_evidence_id={item.id: lineage(item) for item in items},
        candidates=[candidate(item.id, evidence_ids={item.id}, score=1 - i * 0.1) for i, item in enumerate(items)],
    )

    assert len(context.evidence_items) < len(items)
    assert len(context.evidence_items) == 3
