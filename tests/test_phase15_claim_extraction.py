from datetime import datetime, timezone

from roswell_uap_cortex import (
    CandidateClaimOrigin,
    ClaimExtractionEngine,
    ClaimExtractionPolicy,
    ClaimExtractionWarningType,
    ClaimMatrixStatus,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    ObservationType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
)


def raw(text: str) -> RawInput:
    return RawInput(
        input_id="claim-extraction",
        input_type=RawInputType.NOTE,
        title="Synthetic Claim Extraction",
        raw_text=text,
        source_uri="fixture://claim-extraction",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def extract(text: str):
    ingestion = IngestionNormalizer().ingest(raw(text))
    provenance_by_evidence_id = {
        provenance.evidence_id: provenance for provenance in ingestion.provenance_records
    }
    evidence_by_id = {item.id: item for item in ingestion.evidence_items}
    return ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id=evidence_by_id,
        provenance_by_evidence_id=provenance_by_evidence_id,
    )


def test_direct_observation_can_seed_candidate_claim_with_caution() -> None:
    result = extract("The observer saw a bright light moving west.")
    claim = result.candidate_claims[0]

    assert claim.origin is CandidateClaimOrigin.FROM_DIRECT_OBSERVATION
    assert claim.observation_type is ObservationType.DIRECT_OBSERVATION
    assert claim.status is ClaimMatrixStatus.UNSUPPORTED
    assert claim.confidence == 0.0
    assert ClaimExtractionWarningType.DIRECT_OBSERVATION_CAUTION in {
        warning.warning_type for warning in claim.warnings
    }


def test_reported_claim_remains_reported_and_unverified() -> None:
    result = extract("Witness stated that the object hovered silently.")
    claim = result.candidate_claims[0]

    assert claim.origin is CandidateClaimOrigin.FROM_REPORTED_CLAIM
    assert ClaimExtractionWarningType.REPORTED_CLAIM_NOT_VERIFIED in {
        warning.warning_type for warning in claim.warnings
    }


def test_interpretation_becomes_candidate_claim_not_observation() -> None:
    result = extract("The analyst concluded it was an aircraft.")
    claim = result.candidate_claims[0]

    assert claim.origin is CandidateClaimOrigin.FROM_INTERPRETATION
    assert claim.observation_type is ObservationType.INTERPRETATION
    assert ClaimExtractionWarningType.INTERPRETATION_NOT_OBSERVATION in {
        warning.warning_type for warning in claim.warnings
    }


def test_speculation_becomes_speculative_candidate_claim() -> None:
    result = extract("The object might have been an unknown craft.")
    claim = result.candidate_claims[0]

    assert claim.origin is CandidateClaimOrigin.FROM_SPECULATION
    assert claim.speculative
    assert ClaimExtractionWarningType.SPECULATION_REMAINS_SPECULATION in {
        warning.warning_type for warning in claim.warnings
    }


def test_metadata_is_not_extracted_by_default() -> None:
    ingestion = IngestionNormalizer().ingest(
        RawInput(
            input_id="metadata-claim",
            input_type=RawInputType.IMAGE_METADATA,
            title="Synthetic Metadata",
            raw_text="Author: synthetic records office.",
            source_uri="fixture://metadata",
            source_kind="metadata",
            collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        )
    )

    result = ClaimExtractionEngine().extract(ingestion.observations)

    assert result.candidate_claims == []


def test_policy_can_extract_metadata_but_keeps_it_unsupported() -> None:
    ingestion = IngestionNormalizer().ingest(
        RawInput(
            input_id="metadata-claim-policy",
            input_type=RawInputType.IMAGE_METADATA,
            title="Synthetic Metadata",
            raw_text="Author: synthetic records office.",
            source_uri="fixture://metadata-policy",
            source_kind="metadata",
            collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        )
    )
    result = ClaimExtractionEngine(
        ClaimExtractionPolicy(extract_from_metadata=True)
    ).extract(ingestion.observations)
    claim = result.candidate_claims[0]

    assert claim.origin is CandidateClaimOrigin.FROM_METADATA
    assert claim.status is ClaimMatrixStatus.UNSUPPORTED


def test_unknown_observation_does_not_create_candidate_claim() -> None:
    result = extract("Bright object over the field.")

    assert result.candidate_claims == []


def test_candidate_claim_preserves_provenance_and_observation_ids() -> None:
    result = extract("Witness reported that the object moved east.")
    claim = result.candidate_claims[0]

    assert claim.source_observation_id
    assert claim.source_evidence_id
    assert claim.provenance_ids
    assert claim.metadata["extraction_not_confirmation"] is True


def test_extraction_does_not_create_graph_edges_or_confirmations() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="synthetic"))

    result = extract("The analyst concluded it was an aircraft.")
    claim = result.candidate_claims[0]

    assert graph.edges == {}
    assert claim.status is ClaimMatrixStatus.UNSUPPORTED
    assert claim.confidence == 0.0


def test_missing_provenance_warning_is_visible() -> None:
    ingestion = IngestionNormalizer().ingest(raw("The observer saw a bright light."))
    result = ClaimExtractionEngine().extract(ingestion.observations)

    assert ClaimExtractionWarningType.MISSING_PROVENANCE in {
        warning.warning_type for warning in result.warnings
    }


def test_claim_extraction_is_deterministic() -> None:
    first = extract("The object might have been an unknown craft.")
    second = extract("The object might have been an unknown craft.")

    assert [claim.id for claim in first.candidate_claims] == [
        claim.id for claim in second.candidate_claims
    ]
    assert [claim.canonical_topic for claim in first.candidate_claims] == [
        claim.canonical_topic for claim in second.candidate_claims
    ]
