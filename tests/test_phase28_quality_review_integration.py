from datetime import datetime, timezone

from roswell_uap_cortex import (
    ClaimEvaluationWarningType,
    ClaimExtractionEngine,
    ClaimEvidenceEvaluator,
    ClaimNormalizer,
    ClaimReviewEngine,
    ClaimMatrixStatus,
    ClaimNode,
    ContaminationFlagType,
    EvidenceDocketFormatter,
    EvidenceQualityEngine,
    EvidenceQualityLabel,
    EvidenceQualityWarningType,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    LineageType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
    ReviewPriority,
    SourceReviewEngine,
)


def raw(text: str, input_id: str) -> RawInput:
    return RawInput(
        input_id=input_id,
        input_type=RawInputType.NOTE,
        title="Synthetic Phase 28 Fixture",
        raw_text=text,
        source_uri=f"fixture://{input_id}",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def normalized_claim(text: str = "The observer saw a bright light moving west."):
    ingestion = IngestionNormalizer().ingest(raw(text, "phase28-claim"))
    extraction = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    return ClaimNormalizer().normalize(extraction.candidate_claims).normalized_claims[0]


def ingested(text: str, input_id: str):
    result = IngestionNormalizer().ingest(raw(text, input_id))
    return result.evidence_items[0], result


def build_quality_map(evidence_result_pairs, *, fragile: bool = False, contested: bool = False):
    quality = {}
    engine = EvidenceQualityEngine()
    for evidence, result in evidence_result_pairs:
        lineage = result.lineage_records[0]
        if fragile:
            lineage.lineage_type = LineageType.DERIVATIVE_SOURCE
            lineage.derived_from = "parent"
            evidence.metadata["contamination_flags"] = [ContaminationFlagType.SPECULATIVE_LANGUAGE.value]
        quality[evidence.id] = engine.assess(
            evidence,
            provenance=result.provenance_records[0],
            lineage=lineage,
            contradiction_pressure=0.75 if contested else 0.0,
        )
    return quality


def evaluated_docket(texts: list[str], *, fragile_quality: bool = False, contested_quality: bool = False):
    claim = normalized_claim()
    pairs = [ingested(text, f"phase28-evidence-{index}") for index, text in enumerate(texts)]
    evidence_items = [pair[0] for pair in pairs]
    provenance = {
        record.evidence_id: record
        for _, result in pairs
        for record in result.provenance_records
    }
    lineage = {
        record.evidence_id: record
        for _, result in pairs
        for record in result.lineage_records
    }
    quality = build_quality_map(pairs, fragile=fragile_quality, contested=contested_quality)
    evaluation = ClaimEvidenceEvaluator().evaluate(
        [claim],
        evidence_items,
        provenance_by_evidence_id=provenance,
        lineage_by_evidence_id=lineage,
    )
    docket = ClaimReviewEngine().build_docket(
        [claim],
        evaluation,
        provenance_by_evidence_id=provenance,
        lineage_by_evidence_id=lineage,
        evidence_quality_by_evidence_id=quality,
    )
    return docket, claim, quality, pairs


def test_claim_review_docket_includes_evidence_quality_summaries() -> None:
    docket, _, quality, _ = evaluated_docket(["The observer saw a bright light moving west."])
    item = docket.items[0]

    assert item.quality_summaries
    assert item.quality_summaries[0].evidence_id in quality
    assert item.quality_summaries[0].quality_label is EvidenceQualityLabel.STRONG_CONTEXT
    assert EvidenceQualityWarningType.QUALITY_NOT_TRUTH in item.quality_summaries[0].warning_types


def test_quality_fragility_increases_review_priority_without_claim_confidence() -> None:
    strong, strong_claim, _, _ = evaluated_docket(["The observer saw a bright light moving west."])
    fragile, fragile_claim, _, _ = evaluated_docket(
        ["The observer saw a bright light moving west."],
        fragile_quality=True,
    )

    assert fragile.items[0].priority_score > strong.items[0].priority_score
    assert fragile_claim.confidence == strong_claim.confidence == 0.0
    assert fragile.items[0].confidence == strong.items[0].confidence == 0.0


def test_contested_quality_raises_review_pressure_and_preserves_contradiction_visibility() -> None:
    docket, _, _, _ = evaluated_docket(
        ["The observer saw a bright light moving west."],
        contested_quality=True,
    )
    item = docket.items[0]

    assert item.priority in {ReviewPriority.MEDIUM, ReviewPriority.HIGH, ReviewPriority.URGENT}
    assert item.quality_summaries[0].quality_label is EvidenceQualityLabel.CONTESTED
    assert EvidenceQualityWarningType.CONTRADICTION_PRESSURE_VISIBLE in item.quality_summaries[0].warning_types


def test_evidence_docket_formatter_prints_quality_boundary() -> None:
    docket, _, _, _ = evaluated_docket(["The observer saw a bright light moving west."])
    text = EvidenceDocketFormatter().format(docket)

    assert "Evidence quality" in text
    assert "boundary:evidence quality is review context, not claim confirmation" in text
    assert "does not confirm or reject claims" in text


def test_source_review_docket_includes_quality_summaries_without_source_truth() -> None:
    _, _, quality, pairs = evaluated_docket(
        ["The observer saw a bright light moving west."],
        fragile_quality=True,
    )
    evidence_items = [pair[0] for pair in pairs]
    provenance = [record for _, result in pairs for record in result.provenance_records]
    lineage = [record for _, result in pairs for record in result.lineage_records]

    docket = SourceReviewEngine().build_docket(
        evidence_items,
        provenance_records=provenance,
        lineage_records=lineage,
        evidence_quality_by_evidence_id=quality,
    )
    item = docket.items[0]

    assert item.quality_summaries
    assert item.quality_summaries[0].quality_label in {EvidenceQualityLabel.FRAGILE, EvidenceQualityLabel.REVIEWABLE}
    assert any("evidence quality is review context, not source truth" in note for note in item.notes)
    assert item.reliability_score <= 1.0


def test_strong_quality_does_not_confirm_claim_or_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    docket, claim, _, _ = evaluated_docket(["The observer saw a bright light moving west."])
    claim_node = ClaimNode("synthetic claim", "topic", status=ClaimMatrixStatus.UNSUPPORTED, confidence=0.0)

    assert docket.items[0].quality_summaries[0].quality_label is EvidenceQualityLabel.STRONG_CONTEXT
    assert claim.confidence == 0.0
    assert claim_node.status is ClaimMatrixStatus.UNSUPPORTED
    assert graph.edges == {}


def test_quality_warnings_remain_separate_from_claim_evaluation_warnings() -> None:
    docket, _, _, _ = evaluated_docket(
        ["The observer saw a bright light moving west."],
        fragile_quality=True,
    )
    item = docket.items[0]

    assert EvidenceQualityWarningType.CONTAMINATION_RISK_VISIBLE in item.quality_summaries[0].warning_types
    assert ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION not in item.warning_types
