from datetime import datetime, timezone

from roswell_uap_cortex import (
    ClaimEvaluationWarningType,
    ClaimExtractionEngine,
    ClaimEvidenceEvaluator,
    ClaimNormalizer,
    ClaimReviewEngine,
    EvidenceDocketFormatter,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
    ReviewPriority,
    ReviewRecommendationType,
)


def raw(text: str, input_id: str) -> RawInput:
    return RawInput(
        input_id=input_id,
        input_type=RawInputType.NOTE,
        title="Synthetic Review Fixture",
        raw_text=text,
        source_uri=f"fixture://{input_id}",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def normalized_claim(text: str = "The observer saw a bright light moving west."):
    ingestion = IngestionNormalizer().ingest(raw(text, "review-claim"))
    extraction = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    return ClaimNormalizer().normalize(extraction.candidate_claims).normalized_claims[0]


def ingested_evidence(text: str, input_id: str):
    result = IngestionNormalizer().ingest(raw(text, input_id))
    return result.evidence_items[0], result


def evaluated_docket(evidence_texts: list[str], *, include_provenance: bool = True, same_lineage: bool = False):
    claim = normalized_claim()
    evidence_items = []
    provenance = {}
    lineage = {}
    for index, text in enumerate(evidence_texts):
        evidence, result = ingested_evidence(text, f"review-evidence-{index}")
        if same_lineage:
            result.lineage_records[0].lineage_id = "same-line"
            claim.lineage_ids = {"same-line"}
        evidence_items.append(evidence)
        provenance.update({record.evidence_id: record for record in result.provenance_records})
        lineage.update({record.evidence_id: record for record in result.lineage_records})

    evaluation = ClaimEvidenceEvaluator().evaluate(
        [claim],
        evidence_items,
        provenance_by_evidence_id=provenance if include_provenance else {},
        lineage_by_evidence_id=lineage,
    )
    docket = ClaimReviewEngine().build_docket(
        [claim],
        evaluation,
        provenance_by_evidence_id=provenance if include_provenance else {},
        lineage_by_evidence_id=lineage,
    )
    return docket, claim, evaluation


def test_contested_claims_rise_in_review_priority() -> None:
    docket, _, _ = evaluated_docket(["The observer saw no bright light moving west."])
    item = docket.items[0]

    assert item.priority in {ReviewPriority.HIGH, ReviewPriority.URGENT}
    assert item.contradiction_summaries


def test_unsupported_claims_remain_unsupported_and_unmutated() -> None:
    docket, claim, _ = evaluated_docket(["The observer saw a bright light moving west."])

    assert docket.items[0].unsupported
    assert claim.unsupported
    assert claim.confidence == 0.0


def test_support_and_contradiction_stay_separated() -> None:
    docket, _, _ = evaluated_docket(
        [
            "The observer saw a bright light moving west.",
            "The observer saw no bright light moving west.",
        ]
    )
    item = docket.items[0]

    assert item.support_summaries
    assert item.contradiction_summaries
    assert item.support_summaries[0].evidence_id != item.contradiction_summaries[0].evidence_id


def test_same_lineage_support_is_flagged_for_review() -> None:
    docket, _, _ = evaluated_docket(["The observer saw a bright light moving west."], same_lineage=True)
    item = docket.items[0]

    assert ClaimEvaluationWarningType.SAME_LINEAGE_NOT_CORROBORATION in item.warning_types
    assert ReviewRecommendationType.CHECK_SOURCE_INDEPENDENCE in {
        recommendation.recommendation_type for recommendation in item.recommendations
    }


def test_provenance_citations_are_preserved() -> None:
    docket, _, _ = evaluated_docket(["The observer saw a bright light moving west."])

    assert docket.citations
    assert docket.citations[0].evidence_id is not None
    assert docket.citations[0].provenance_id is not None


def test_missing_provenance_increases_review_priority() -> None:
    with_provenance, _, _ = evaluated_docket(["The observer saw a bright light moving west."])
    missing, _, _ = evaluated_docket(["The observer saw a bright light moving west."], include_provenance=False)

    assert missing.items[0].priority_score > with_provenance.items[0].priority_score
    assert ReviewRecommendationType.VERIFY_PROVENANCE in {
        recommendation.recommendation_type for recommendation in missing.items[0].recommendations
    }


def test_speculative_and_reported_evidence_remain_labeled() -> None:
    docket, _, _ = evaluated_docket(
        [
            "The object might have been a bright light moving west.",
            "Witness reported that the observer saw a bright light moving west.",
        ]
    )
    warning_types = set(docket.items[0].warning_types)

    assert ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION in warning_types
    assert ClaimEvaluationWarningType.REPORTED_CLAIM_CAUTION in warning_types


def test_review_queue_ordering_is_deterministic() -> None:
    low, _, _ = evaluated_docket(["The observer saw a bright light moving west."])
    high, _, _ = evaluated_docket(["The observer saw no bright light moving west."])
    queue_a = ClaimReviewEngine().build_queue([low, high])
    queue_b = ClaimReviewEngine().build_queue([high, low])

    assert [docket.docket_id for docket in queue_a.dockets] == [docket.docket_id for docket in queue_b.dockets]
    assert queue_a.dockets[0].items[0].priority_score >= queue_a.dockets[1].items[0].priority_score


def test_formatter_keeps_review_language_bounded() -> None:
    docket, _, _ = evaluated_docket(["The observer saw no bright light moving west."])
    text = EvidenceDocketFormatter().format(docket)

    assert "does not confirm or reject claims" in text
    assert "Possible contradiction" in text
    assert "Unsupported remains unsupported: true" in text


def test_review_engine_does_not_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))

    evaluated_docket(["The observer saw a bright light moving west."])

    assert graph.edges == {}
