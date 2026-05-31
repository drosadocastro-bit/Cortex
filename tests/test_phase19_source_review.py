from datetime import datetime, timezone

from roswell_uap_cortex import (
    ClaimExtractionEngine,
    ClaimEvidenceEvaluator,
    ClaimNormalizer,
    ContaminationFlagType,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    LineageType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
    SourceReviewEngine,
    SourceReviewFormatter,
    SourceReviewPriority,
    SourceReviewRecommendationType,
    SourceTrust,
    SourceTrustEngine,
)


def raw(
    text: str,
    input_id: str,
    *,
    source_uri: str | None = None,
    source_kind: str = "note",
    metadata: dict | None = None,
) -> RawInput:
    return RawInput(
        input_id=input_id,
        input_type=RawInputType.NOTE,
        title="Synthetic Source Review",
        raw_text=text,
        source_uri=source_uri or f"fixture://{input_id}",
        source_kind=source_kind,
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        metadata=metadata or {},
    )


def ingest_many(*inputs: RawInput):
    normalizer = IngestionNormalizer()
    results = [normalizer.ingest(item) for item in inputs]
    evidence = [item for result in results for item in result.evidence_items]
    provenance = [record for result in results for record in result.provenance_records]
    lineage = [record for result in results for record in result.lineage_records]
    contamination = [flag for result in results for flag in result.contamination_flags]
    return evidence, provenance, lineage, contamination


def test_source_records_group_by_source_id() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("Observer saw a light.", "source-a-1", source_uri="fixture://shared"),
        raw("Observer recorded a second note.", "source-a-2", source_uri="fixture://shared"),
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )

    assert len(docket.items) == 1
    assert docket.items[0].source_id == "fixture://shared"
    assert len(docket.items[0].evidence_ids) == 2


def test_provenance_gaps_increase_source_risk() -> None:
    evidence, provenance, lineage, contamination = ingest_many(raw("Observer saw a light.", "prov-gap"))
    with_provenance = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )
    missing = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=[],
        lineage_records=lineage,
        contamination_flags=contamination,
    )

    assert missing.items[0].risk_score > with_provenance.items[0].risk_score
    assert SourceReviewRecommendationType.VERIFY_PROVENANCE in {
        recommendation.recommendation_type for recommendation in missing.items[0].recommendations
    }


def test_derivative_lineage_is_flagged() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("Primary note.", "source-primary", source_uri="fixture://primary"),
        raw(
            "Derivative repost note.",
            "source-derivative",
            source_uri="fixture://derivative",
            source_kind="repost",
            metadata={"parent_source_id": "fixture://primary"},
        ),
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )
    derivative_item = next(item for item in docket.items if item.source_id == "fixture://derivative")

    assert any(signal.signal_type == "derivative_lineage" for signal in derivative_item.risk_signals)
    assert LineageType.DERIVATIVE_SOURCE in {record.lineage_type for record in lineage}


def test_repeated_source_uri_is_flagged() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("First shared source note.", "repeat-a", source_uri="fixture://repeat"),
        raw("Second shared source note.", "repeat-b", source_uri="fixture://repeat"),
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )

    assert any(signal.signal_type == "repeated_source_uri" for signal in docket.items[0].risk_signals)


def test_contamination_flags_appear_in_source_review() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("Maybe this involved a lightsaber.", "contaminated", source_uri="fixture://contaminated")
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )

    assert ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS in docket.items[0].contamination_flags
    assert any(signal.signal_type == "contamination_flags" for signal in docket.items[0].risk_signals)


def test_speculative_and_reported_content_affect_risk() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("The object might have been a bright light.", "spec-source"),
        raw("Witness reported that a bright light was seen.", "reported-source"),
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )
    signal_types = {signal.signal_type for item in docket.items for signal in item.risk_signals}

    assert "speculative_content" in signal_types
    assert "reported_claim_content" in signal_types


def test_source_trust_affects_reliability_without_deciding_truth() -> None:
    evidence, provenance, lineage, contamination = ingest_many(raw("Observer saw a light.", "trusted-source"))
    trust = SourceTrustEngine().evaluate(
        SourceTrust(
            source_id=evidence[0].source_id,
            reliability=0.9,
            transparency=0.9,
            chain_of_custody=0.9,
            media_type="archival_document",
        )
    )

    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
        source_trust_records=[trust],
    )

    assert any(signal.signal_type == "source_trust_inputs" for signal in docket.items[0].reliability_signals)
    assert "truth" in " ".join(docket.notes)


def test_claim_assessments_can_reference_source_risk_without_confirming_claims() -> None:
    evidence, provenance, lineage, contamination = ingest_many(raw("The observer saw a bright light.", "claim-source"))
    extraction = ClaimExtractionEngine().extract(
        [ ],
        evidence_by_id={},
        provenance_by_evidence_id={},
    )
    assert extraction.candidate_claims == []

    ingestion = IngestionNormalizer().ingest(raw("The observer saw a bright light.", "claim-eval-source"))
    candidate = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    normalized = ClaimNormalizer().normalize(candidate.candidate_claims).normalized_claims
    evaluation = ClaimEvidenceEvaluator().evaluate(
        normalized,
        evidence,
        provenance_by_evidence_id={record.evidence_id: record for record in provenance},
        lineage_by_evidence_id={record.evidence_id: record for record in lineage},
    )
    docket = SourceReviewEngine().build_docket(evidence, provenance_records=provenance, lineage_records=lineage)

    assert evaluation.assessments
    assert normalized[0].unsupported
    assert docket.items[0].source_id == evidence[0].source_id


def test_source_review_does_not_mutate_records_or_create_graph_edges() -> None:
    evidence, provenance, lineage, contamination = ingest_many(raw("Observer saw a light.", "nomutate-source"))
    before_metadata = dict(evidence[0].metadata)
    trust = SourceTrust(source_id=evidence[0].source_id, source_trust_score=0.8, source_risk_score=0.2)
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.SOURCE, label="source"))

    SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
        source_trust_records=[trust],
    )

    assert evidence[0].metadata == before_metadata
    assert trust.source_trust_score == 0.8
    assert graph.edges == {}


def test_formatter_avoids_certainty_inflation() -> None:
    evidence, provenance, lineage, contamination = ingest_many(raw("Maybe a lightsaber was seen.", "format-source"))
    docket = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )
    text = SourceReviewFormatter().format(docket)

    assert "Source review is not source truth" in text
    assert "Risk signals" in text


def test_source_review_ordering_is_deterministic() -> None:
    evidence, provenance, lineage, contamination = ingest_many(
        raw("Maybe a lightsaber was seen.", "ordered-risk"),
        raw("Observer saw a light.", "ordered-clean"),
    )

    first = SourceReviewEngine().build_docket(
        evidence,
        provenance_records=provenance,
        lineage_records=lineage,
        contamination_flags=contamination,
    )
    second = SourceReviewEngine().build_docket(
        list(reversed(evidence)),
        provenance_records=list(reversed(provenance)),
        lineage_records=list(reversed(lineage)),
        contamination_flags=list(reversed(contamination)),
    )

    assert [item.source_id for item in first.items] == [item.source_id for item in second.items]
    assert first.items[0].priority_score >= first.items[-1].priority_score
    assert first.docket_id == second.docket_id
