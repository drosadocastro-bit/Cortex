from roswell_uap_cortex import (
    ActivatedContext,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    CitationFormatter,
    DiscourseGuardrails,
    DiscourseRequest,
    DiscourseWarningType,
    EvidenceItem,
    NarrativeBuilder,
    ProvenanceRecord,
    ReasoningObservation,
    ReasoningOutput,
    ReasoningWarning,
    ReasoningWarningType,
    SourceLineageRecord,
)
from roswell_uap_cortex.cli import build_demo_discourse
from roswell_uap_cortex.discourse import DiscourseEngine


def evidence_item(evidence_id: str = "e1", *, flags: list[str] | None = None) -> EvidenceItem:
    return EvidenceItem(
        id=evidence_id,
        summary="Synthetic observed evidence",
        source_id="synthetic://source",
        evidence_type="note",
        metadata={"lineage_id": "line-1", "contamination_flags": flags or []},
    )


def provenance(item: EvidenceItem) -> ProvenanceRecord:
    return ProvenanceRecord(
        evidence_id=item.id,
        source_uri=item.source_id,
        source_kind="synthetic_note",
        ingestion_method="test",
        extraction_method="test",
        original_input_id="input-1",
        page_number=2,
    )


def lineage(item: EvidenceItem) -> SourceLineageRecord:
    return SourceLineageRecord(
        evidence_id=item.id,
        source_id=item.source_id,
        lineage_id=item.metadata["lineage_id"],
        source_uri=item.source_id,
    )


def build_response(reasoning: ReasoningOutput, activated: ActivatedContext | None = None):
    item = evidence_item()
    return DiscourseEngine().build(
        DiscourseRequest(
            query="synthetic query",
            activated_context=activated or ActivatedContext(activated_evidence_ids={item.id}),
            reasoning_output=reasoning,
        ),
        evidence_by_id={item.id: item},
        provenance_by_evidence_id={item.id: provenance(item)},
        lineage_by_evidence_id={item.id: lineage(item)},
    )


def test_discourse_preserves_contradictions() -> None:
    reasoning = ReasoningOutput(contested_context_ids={"claim-1"}, requires_review=True)
    response = build_response(reasoning)

    assert response.contradictions.items == [
        "Unresolved contradiction or contested context: claim-1"
    ]
    assert response.review_required is True
    assert DiscourseWarningType.CONTRADICTION_VISIBLE in {
        warning.warning_type for warning in response.observed_evidence.warnings
    }


def test_speculative_hypotheses_remain_labeled() -> None:
    reasoning = ReasoningOutput(
        possible_hypotheses=[
            ReasoningObservation(text="possible relation only", context_ids={"e1"}, speculative=True)
        ]
    )
    response = build_response(reasoning)

    assert response.speculative_hypotheses.items == [
        "Speculative: possible relation only"
    ]
    assert "Speculative hypotheses:" in response.narrative.speculation


def test_unsupported_claims_remain_unsupported() -> None:
    reasoning = ReasoningOutput(
        reasoning_warnings=[
            ReasoningWarning(
                warning_type=ReasoningWarningType.UNSUPPORTED_CLAIM,
                message="Unsupported claim remains unsupported.",
                related_ids={"claim-u"},
            )
        ]
    )
    response = build_response(reasoning)

    assert DiscourseWarningType.UNSUPPORTED_REMAINS_UNSUPPORTED in {
        warning.warning_type for warning in response.observed_evidence.warnings
    }


def test_provenance_citations_appear_in_output() -> None:
    reasoning = ReasoningOutput(
        observations=[ReasoningObservation(text="Observed note", context_ids={"e1"})],
        supporting_context_ids={"e1"},
        provenance_summary="1/1 evidence items include provenance.",
    )
    response = build_response(reasoning)

    assert response.citations
    assert "evidence:e1" in response.citations[0].label
    assert "page:2" in response.citations[0].label


def test_missing_provenance_generates_uncertainty_notes() -> None:
    item = evidence_item()
    reasoning = ReasoningOutput(
        observations=[ReasoningObservation(text="Observed note", context_ids={item.id})],
        reasoning_warnings=[
            ReasoningWarning(
                warning_type=ReasoningWarningType.MISSING_PROVENANCE,
                message="Some evidence lacks provenance records.",
                related_ids={item.id},
            )
        ],
    )
    response = DiscourseEngine().build(
        DiscourseRequest(
            query="missing",
            activated_context=ActivatedContext(activated_evidence_ids={item.id}),
            reasoning_output=reasoning,
        ),
        evidence_by_id={item.id: item},
    )

    assert "Some evidence lacks provenance records." in response.missing_information.items
    assert response.review_required is True


def test_duplicate_citations_are_merged() -> None:
    item = evidence_item()
    first = CitationFormatter().citation_for(
        item.id,
        provenance=provenance(item),
        lineage=lineage(item),
        source_id=item.source_id,
    )
    second = CitationFormatter().citation_for(
        item.id,
        provenance=provenance(item),
        lineage=lineage(item),
        source_id=item.source_id,
    )

    merged = CitationFormatter().merge([first, second])

    assert len(merged) == 1


def test_narrative_builder_separates_observations_from_speculation() -> None:
    reasoning = ReasoningOutput(
        observations=[ReasoningObservation(text="Observed note", context_ids={"e1"})],
        possible_hypotheses=[
            ReasoningObservation(text="possible relation only", context_ids={"e1"}, speculative=True)
        ],
    )
    response = build_response(reasoning)
    narrative = NarrativeBuilder().build(response)

    assert "Observed note" in narrative.observations
    assert "possible relation only" in narrative.speculation
    assert "possible relation only" not in narrative.observations


def test_discourse_never_fabricates_evidence() -> None:
    reasoning = ReasoningOutput(
        observations=[ReasoningObservation(text="Observed note", context_ids={"missing-evidence"})]
    )
    response = build_response(reasoning)

    assert response.citations == []
    assert DiscourseWarningType.NO_FABRICATED_EVIDENCE in {
        warning.warning_type for warning in response.observed_evidence.warnings
    }


def test_cli_produces_deterministic_output() -> None:
    first = build_demo_discourse("bright object")
    second = build_demo_discourse("bright object")

    assert first == second
    assert "## Observed Evidence" in first
    assert "## Citations" in first


def test_contradiction_visibility_is_preserved() -> None:
    activated = ActivatedContext(
        contested_associations=[
            AssociationCandidate(
                record_id="claim-c",
                record_type="claim",
                label="contested claim",
                score=AssociationScore(final_association_score=0.8),
                association_label=AssociationLabel.CONTESTED_ASSOCIATION,
            )
        ]
    )
    reasoning = ReasoningOutput(contested_context_ids={"claim-c"})
    response = build_response(reasoning, activated)

    assert response.possible_associations.items == [
        "Possible association: contested claim"
    ]
    assert response.contradictions.items


def test_discourse_warnings_appear_for_contamination_flags() -> None:
    reasoning = ReasoningOutput(
        reasoning_warnings=[
            ReasoningWarning(
                warning_type=ReasoningWarningType.FICTIONAL_CONTAMINATION,
                message="Fictional contamination terms were present.",
                related_ids={"e1"},
            )
        ]
    )
    response = build_response(reasoning)

    assert DiscourseWarningType.CONTAMINATION_WARNING in {
        warning.warning_type for warning in response.observed_evidence.warnings
    }


def test_discourse_remains_bounded_and_explainable() -> None:
    reasoning = ReasoningOutput(
        observations=[ReasoningObservation(text=f"Observation {index}", context_ids={"e1"}) for index in range(3)],
        possible_hypotheses=[
            ReasoningObservation(text="possible relation only", context_ids={"e1"}, speculative=True)
        ],
        provenance_summary="1/1 evidence items include provenance.",
    )
    response = build_response(reasoning)

    assert len(response.observed_evidence.items) == 3
    assert response.provenance_notes.items == ["1/1 evidence items include provenance."]
    assert all("confirmed" not in item.casefold() for item in response.observed_evidence.items)
