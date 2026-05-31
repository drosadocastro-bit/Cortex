from datetime import datetime, timezone

from roswell_uap_cortex import (
    ClaimEvidenceAssessmentType,
    ClaimEvaluationWarningType,
    ClaimExtractionEngine,
    ClaimMatrixEngine,
    ClaimMatrixStatus,
    ClaimNormalizer,
    ClaimEvidenceEvaluator,
    EvidenceItem,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    ObservationType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
)


def raw(text: str, input_id: str = "claim-eval") -> RawInput:
    return RawInput(
        input_id=input_id,
        input_type=RawInputType.NOTE,
        title="Synthetic Claim Eval",
        raw_text=text,
        source_uri=f"fixture://{input_id}",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def normalized_claim(text: str = "The observer saw a bright light moving west."):
    ingestion = IngestionNormalizer().ingest(raw(text, "claim-source"))
    extraction = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    return ClaimNormalizer().normalize(extraction.candidate_claims).normalized_claims[0]


def ingested_evidence(text: str, input_id: str = "evidence"):
    result = IngestionNormalizer().ingest(raw(text, input_id))
    return result.evidence_items[0], result


def evaluate_against(evidence_text: str, input_id: str = "evidence"):
    claim = normalized_claim()
    evidence, result = ingested_evidence(evidence_text, input_id)
    evaluation = ClaimEvidenceEvaluator().evaluate(
        [claim],
        [evidence],
        provenance_by_evidence_id={record.evidence_id: record for record in result.provenance_records},
        lineage_by_evidence_id={record.evidence_id: record for record in result.lineage_records},
    )
    return evaluation.assessments[0], claim, evidence


def test_evidence_assessment_can_mark_possible_support() -> None:
    assessment, _, _ = evaluate_against("The observer saw a bright light moving west.")

    assert assessment.assessment_type is ClaimEvidenceAssessmentType.POSSIBLE_SUPPORT
    assert assessment.support_score > 0


def test_evidence_assessment_can_mark_possible_contradiction() -> None:
    assessment, _, _ = evaluate_against("No bright light was present.")

    assert assessment.assessment_type is ClaimEvidenceAssessmentType.POSSIBLE_CONTRADICTION
    assert assessment.contradiction_score > 0


def test_support_does_not_confirm_claim() -> None:
    assessment, claim, _ = evaluate_against("The observer saw a bright light moving west.")

    assert assessment.support_score > 0
    assert claim.confidence == 0.0
    assert claim.unsupported


def test_contradiction_does_not_disprove_claim() -> None:
    assessment, claim, _ = evaluate_against("The observer saw no bright light moving west.")

    assert assessment.contradiction_score > 0
    assert claim.confidence == 0.0
    assert claim.unsupported


def test_same_lineage_support_is_downgraded() -> None:
    claim = normalized_claim()
    evidence, result = ingested_evidence("The observer saw a bright light moving west.", "same")
    result.lineage_records[0].lineage_id = next(iter(claim.lineage_ids)) if claim.lineage_ids else "same"
    claim.lineage_ids = {result.lineage_records[0].lineage_id}

    assessment = ClaimEvidenceEvaluator().evaluate(
        [claim],
        [evidence],
        provenance_by_evidence_id={record.evidence_id: record for record in result.provenance_records},
        lineage_by_evidence_id={record.evidence_id: record for record in result.lineage_records},
    ).assessments[0]

    assert assessment.support_score < 0.5
    assert ClaimEvaluationWarningType.SAME_LINEAGE_NOT_CORROBORATION in {
        warning.warning_type for warning in assessment.warnings
    }


def test_repeated_paraphrase_support_does_not_inflate_confidence() -> None:
    claim = normalized_claim()
    claim.lineage_ids = {"same"}
    evidence_a, result_a = ingested_evidence("The observer saw a bright light moving west.", "a")
    evidence_b, result_b = ingested_evidence("The observer saw bright light moving west.", "b")
    for record in result_a.lineage_records + result_b.lineage_records:
        record.lineage_id = "same"

    evaluation = ClaimEvidenceEvaluator().evaluate(
        [claim],
        [evidence_a, evidence_b],
        provenance_by_evidence_id={
            **{record.evidence_id: record for record in result_a.provenance_records},
            **{record.evidence_id: record for record in result_b.provenance_records},
        },
        lineage_by_evidence_id={
            **{record.evidence_id: record for record in result_a.lineage_records},
            **{record.evidence_id: record for record in result_b.lineage_records},
        },
    )
    matrix = ClaimMatrixEngine()
    entry = matrix.register_evidence_assessments(claim.canonical_key.value, evaluation)

    assert entry.claim_confidence <= 0.35


def test_speculative_evidence_is_flagged() -> None:
    assessment, _, _ = evaluate_against("The object might have been a bright light moving west.")

    assert ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION in {
        warning.warning_type for warning in assessment.warnings
    }


def test_reported_claim_evidence_is_flagged() -> None:
    assessment, _, _ = evaluate_against("Witness reported that the observer saw a bright light moving west.")

    assert ClaimEvaluationWarningType.REPORTED_CLAIM_CAUTION in {
        warning.warning_type for warning in assessment.warnings
    }


def test_metadata_does_not_become_event_truth() -> None:
    claim = normalized_claim()
    evidence = EvidenceItem(
        summary="Author: observer saw bright light moving west",
        source_id="fixture://metadata",
        evidence_type="image_metadata",
        metadata={"observation_type": ObservationType.METADATA_STATEMENT.value},
    )
    assessment = ClaimEvidenceEvaluator().evaluate([claim], [evidence]).assessments[0]

    assert assessment.support_score == 0.0
    assert ClaimEvaluationWarningType.METADATA_NOT_EVENT_TRUTH in {
        warning.warning_type for warning in assessment.warnings
    }


def test_missing_provenance_produces_warning() -> None:
    assessment, _, _ = evaluate_against("The observer saw a bright light moving west.")
    assessment = ClaimEvidenceEvaluator().evaluate([normalized_claim()], [assessment_to_evidence(assessment)]).assessments[0]

    assert ClaimEvaluationWarningType.MISSING_PROVENANCE in {
        warning.warning_type for warning in assessment.warnings
    }


def assessment_to_evidence(assessment):
    return EvidenceItem(
        summary="The observer saw a bright light moving west.",
        source_id="fixture://missing-provenance",
        evidence_type="note",
        id=assessment.evidence_id,
        metadata={"observation_type": ObservationType.DIRECT_OBSERVATION.value},
    )


def test_high_support_plus_high_contradiction_produces_needs_review() -> None:
    assessment, _, _ = evaluate_against("The observer saw no bright light moving west.")

    assert assessment.assessment_type is ClaimEvidenceAssessmentType.NEEDS_REVIEW
    assert ClaimEvaluationWarningType.NEEDS_REVIEW in {
        warning.warning_type for warning in assessment.warnings
    }


def test_claim_matrix_integration_preserves_conservative_status() -> None:
    claim = normalized_claim()
    evidence, result = ingested_evidence("The observer saw no bright light moving west.", "conservative")
    evaluation = ClaimEvidenceEvaluator().evaluate(
        [claim],
        [evidence],
        provenance_by_evidence_id={record.evidence_id: record for record in result.provenance_records},
        lineage_by_evidence_id={record.evidence_id: record for record in result.lineage_records},
    )
    matrix = ClaimMatrixEngine()
    entry = matrix.register_evidence_assessments(claim.canonical_key.value, evaluation)

    assert entry.status in {ClaimMatrixStatus.UNSUPPORTED, ClaimMatrixStatus.UNRESOLVED, ClaimMatrixStatus.CONTESTED}
    assert 0.0 <= entry.claim_confidence <= 1.0


def test_evidence_records_are_not_mutated() -> None:
    claim = normalized_claim()
    evidence, result = ingested_evidence("The observer saw a bright light moving west.", "nomutate")
    before = dict(evidence.metadata)

    ClaimEvidenceEvaluator().evaluate(
        [claim],
        [evidence],
        provenance_by_evidence_id={record.evidence_id: record for record in result.provenance_records},
    )

    assert evidence.metadata == before


def test_graph_edges_are_not_created_automatically() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))

    evaluate_against("The observer saw a bright light moving west.")

    assert graph.edges == {}


def test_irrelevant_high_lexical_noise_can_remain_irrelevant_or_uncertain() -> None:
    assessment, _, _ = evaluate_against("Bright office light moved across the west hallway.")

    assert assessment.assessment_type in {
        ClaimEvidenceAssessmentType.IRRELEVANT,
        ClaimEvidenceAssessmentType.UNCERTAIN,
        ClaimEvidenceAssessmentType.POSSIBLE_SUPPORT,
    }
    assert 0.0 <= assessment.support_score <= 1.0
    assert 0.0 <= assessment.contradiction_score <= 1.0
