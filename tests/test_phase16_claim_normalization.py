from datetime import datetime, timezone

from roswell_uap_cortex import (
    CandidateClaimOrigin,
    ClaimExtractionEngine,
    ClaimMatrixEngine,
    ClaimMatrixIntegrator,
    ClaimMatrixStatus,
    ClaimNormalizationPolicy,
    ClaimNormalizationWarningType,
    ClaimNormalizer,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    ObservationType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
)


def raw(text: str, input_id: str = "normalize") -> RawInput:
    return RawInput(
        input_id=input_id,
        input_type=RawInputType.NOTE,
        title="Synthetic Normalization",
        raw_text=text,
        source_uri=f"fixture://{input_id}",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        metadata={"lineage_id": f"lineage-{input_id}"},
    )


def candidates_from(text: str, input_id: str = "normalize"):
    ingestion = IngestionNormalizer().ingest(raw(text, input_id))
    evidence_by_id = {item.id: item for item in ingestion.evidence_items}
    provenance_by_id = {record.evidence_id: record for record in ingestion.provenance_records}
    extraction = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id=evidence_by_id,
        provenance_by_evidence_id=provenance_by_id,
    )
    for claim in extraction.candidate_claims:
        claim.metadata["lineage_id"] = f"lineage-{input_id}"
    return extraction.candidate_claims


def test_candidate_claims_normalize_into_canonical_groups() -> None:
    claims = candidates_from("The observer saw a bright light moving west.", "a")
    claims += candidates_from("The observer saw bright light moving west.", "b")

    result = ClaimNormalizer().normalize(claims)

    assert len(result.normalized_claims) == 1
    assert result.normalized_claims[0].canonical_key.value == "bright-light-moving-observer-saw-west"


def test_normalization_preserves_candidate_ids_evidence_and_provenance() -> None:
    claims = candidates_from("Witness reported that the object moved east.", "a")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims[0]

    assert normalized.candidate_claim_ids == {claims[0].id}
    assert normalized.evidence_ids == {claims[0].source_evidence_id}
    assert normalized.provenance_ids == claims[0].provenance_ids


def test_normalization_preserves_lineage_ids() -> None:
    claims = candidates_from("Witness reported that the object moved east.", "lineage-a")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims[0]

    assert normalized.lineage_ids == {"lineage-lineage-a"}


def test_same_lineage_repeated_claims_are_flagged() -> None:
    claims = candidates_from("Witness reported that the object moved east.", "same-a")
    claims += candidates_from("Witness reported that the object moved east.", "same-b")
    for claim in claims:
        claim.metadata["lineage_id"] = "same-lineage"

    normalized = ClaimNormalizer().normalize(claims).normalized_claims[0]

    assert ClaimNormalizationWarningType.SAME_LINEAGE_REPETITION in {
        warning.warning_type for warning in normalized.warning_flags
    }


def test_repeated_claims_do_not_increase_confidence() -> None:
    claims = candidates_from("Witness reported that the object moved east.", "a")
    claims += candidates_from("Witness reported that the object moved east.", "b")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims[0]

    assert normalized.confidence == 0.0
    assert normalized.unsupported


def test_speculative_and_reported_origins_remain_visible() -> None:
    claims = candidates_from("Witness reported that the object moved east.", "reported")
    claims += candidates_from("The object might have moved east.", "speculative")

    result = ClaimNormalizer(ClaimNormalizationPolicy(allow_cross_origin_merge=True)).normalize(claims)
    origin_types = set().union(*(claim.origin_types for claim in result.normalized_claims))

    assert CandidateClaimOrigin.FROM_REPORTED_CLAIM in origin_types
    assert CandidateClaimOrigin.FROM_SPECULATION in origin_types


def test_metadata_origin_does_not_become_event_truth() -> None:
    ingestion = IngestionNormalizer().ingest(
        RawInput(
            input_id="metadata",
            input_type=RawInputType.IMAGE_METADATA,
            title="Metadata",
            raw_text="Author: synthetic records office.",
            source_uri="fixture://metadata",
            source_kind="metadata",
            collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        )
    )
    claim = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    assert claim.candidate_claims == []


def test_ambiguous_origin_merges_produce_warnings_when_policy_allows() -> None:
    direct = candidates_from("The observer saw a bright light moving west.", "direct")[0]
    reported = candidates_from("Witness reported that observer saw bright light moving west.", "reported")[0]
    result = ClaimNormalizer(ClaimNormalizationPolicy(allow_cross_origin_merge=True)).normalize([direct, reported])

    assert any(
        ClaimNormalizationWarningType.AMBIGUOUS_ORIGIN_MERGE
        in {warning.warning_type for warning in claim.warning_flags}
        for claim in result.normalized_claims
    )


def test_claim_matrix_integration_registers_unsupported_candidate_topics() -> None:
    claims = candidates_from("The observer saw a bright light moving west.", "matrix")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims
    engine = ClaimMatrixEngine()
    integration = ClaimMatrixIntegrator(engine).integrate(normalized)
    entry = engine.entries[next(iter(integration.registered_topics))]

    assert entry.status is ClaimMatrixStatus.UNSUPPORTED
    assert entry.claim_confidence == 0.0
    assert entry.claims[0].metadata["integration_not_support"] is True


def test_claim_matrix_integration_does_not_create_support_evidence() -> None:
    claims = candidates_from("The observer saw a bright light moving west.", "supportless")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims
    engine = ClaimMatrixEngine()
    ClaimMatrixIntegrator(engine).integrate(normalized)
    entry = next(iter(engine.entries.values()))

    assert entry.supporting_evidence == []
    assert entry.contradicting_evidence == []


def test_claim_matrix_integration_does_not_create_graph_edges_or_mutate_evidence() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    ingestion = IngestionNormalizer().ingest(raw("The observer saw a bright light moving west.", "nomutate"))
    original_metadata = dict(ingestion.evidence_items[0].metadata)
    claims = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    ).candidate_claims

    normalized = ClaimNormalizer().normalize(claims).normalized_claims
    ClaimMatrixIntegrator().integrate(normalized)

    assert graph.edges == {}
    assert ingestion.evidence_items[0].metadata == original_metadata


def test_existing_claim_matrix_behavior_remains_backward_compatible() -> None:
    engine = ClaimMatrixEngine()
    entry = engine.add_claim(
        __import__("roswell_uap_cortex").ClaimNode(
            text="unsupported assertion",
            canonical_topic="unsupported",
        )
    )

    assert entry.status is ClaimMatrixStatus.UNSUPPORTED
    assert entry.claim_confidence == 0.0


def test_all_normalized_confidence_values_remain_bounded() -> None:
    claims = candidates_from("The object might have been a balloon.", "bounded")
    normalized = ClaimNormalizer().normalize(claims).normalized_claims

    assert all(0.0 <= claim.confidence <= 1.0 for claim in normalized)
    assert all(claim.confidence == 0.0 for claim in normalized)
