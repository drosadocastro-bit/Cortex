from datetime import datetime, timezone

from roswell_uap_cortex import (
    ExtractedObservation,
    IngestionNormalizer,
    ObservationClassifier,
    ObservationType,
    RawInput,
    RawInputType,
)


def raw(text: str, input_type: RawInputType = RawInputType.NOTE) -> RawInput:
    return RawInput(
        input_id="observation-boundary",
        input_type=input_type,
        title="Synthetic Observation Boundary",
        raw_text=text,
        source_uri="fixture://observation-boundary",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def classify(text: str, input_type: RawInputType = RawInputType.NOTE) -> ExtractedObservation:
    return ObservationClassifier().classify(
        ExtractedObservation(input_id="x", text=text, sequence=0),
        input_type,
    )


def test_direct_observation_is_classified_without_truth_claim() -> None:
    observation = classify("The witness saw a bright light moving west.")

    assert observation.observation_type is ObservationType.DIRECT_OBSERVATION
    assert "direct observation markers present" in observation.classification_notes


def test_interpretation_is_not_promoted_to_direct_observation() -> None:
    observation = classify("The object was an aircraft because it moved steadily.")

    assert observation.observation_type is ObservationType.INTERPRETATION
    assert observation.interpretation_markers


def test_speculation_remains_speculation() -> None:
    observation = classify("The object might have been an unknown craft.")

    assert observation.observation_type is ObservationType.SPECULATION
    assert observation.speculation_markers


def test_reported_claim_remains_reported_claim_not_verified_observation() -> None:
    observation = classify("Witness stated that the object hovered silently.")

    assert observation.observation_type is ObservationType.REPORTED_CLAIM
    assert observation.reported_speech_markers


def test_metadata_statement_is_separated_from_observation() -> None:
    observation = classify("Author: synthetic records office.", RawInputType.IMAGE_METADATA)

    assert observation.observation_type is ObservationType.METADATA_STATEMENT
    assert "not treated as direct observation" in " ".join(observation.classification_notes)


def test_ambiguous_span_remains_unknown_with_notes() -> None:
    observation = classify("Bright object over the field.")

    assert observation.observation_type is ObservationType.UNKNOWN
    assert "no deterministic observation classification marker" in observation.classification_notes


def test_mixed_markers_choose_cautionary_type_and_record_note() -> None:
    observation = classify("Witness reported that the object might have been an aircraft.")

    assert observation.observation_type is ObservationType.SPECULATION
    assert "mixed markers present; strongest cautionary type selected" in observation.classification_notes


def test_ingestion_carries_observation_classification_into_evidence_metadata() -> None:
    result = IngestionNormalizer().ingest(raw("Witness stated that the light might have been a balloon."))
    evidence = result.evidence_items[0]
    observation = result.observations[0]

    assert observation.observation_type is ObservationType.SPECULATION
    assert evidence.metadata["observation_type"] == ObservationType.SPECULATION.value
    assert evidence.metadata["speculation_markers"]
    assert evidence.metadata["reported_speech_markers"]


def test_ingestion_separates_multiple_observation_types_deterministically() -> None:
    result = IngestionNormalizer().ingest(
        raw(
            "The observer saw a bright light. "
            "The analyst concluded it was an aircraft. "
            "It might have been a balloon."
        )
    )

    assert [observation.observation_type for observation in result.observations] == [
        ObservationType.DIRECT_OBSERVATION,
        ObservationType.INTERPRETATION,
        ObservationType.SPECULATION,
    ]
    assert [item.metadata["observation_type"] for item in result.evidence_items] == [
        ObservationType.DIRECT_OBSERVATION.value,
        ObservationType.INTERPRETATION.value,
        ObservationType.SPECULATION.value,
    ]


def test_observation_classification_does_not_create_claim_confirmation() -> None:
    result = IngestionNormalizer().ingest(raw("The analyst concluded it was an aircraft."))

    assert not hasattr(result, "claims")
    assert all(item.confidence == 0.5 for item in result.evidence_items)
    assert result.evidence_items[0].metadata["observation_type"] == ObservationType.INTERPRETATION.value
