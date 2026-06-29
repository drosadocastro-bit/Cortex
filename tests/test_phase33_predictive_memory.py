from datetime import datetime, timezone

from roswell_uap_cortex import (
    AttentionEngine,
    ExpectationGuardrails,
    MemoryRecord,
    PredictiveMemoryEngine,
    PredictiveReviewAdapter,
    PredictiveSignalType,
    PredictiveWarningType,
)


AS_OF = datetime(2026, 6, 29, tzinfo=timezone.utc)
OLD_DATE = datetime(2026, 5, 1, tzinfo=timezone.utc)


def snapshot(memory: MemoryRecord) -> tuple[object, ...]:
    return (
        memory.memory_strength,
        memory.strength,
        memory.archival,
        memory.access_count,
        memory.activation_count,
        memory.contradiction_pressure,
        memory.needs_review,
        tuple(sorted(memory.evidence_ids)),
        tuple(memory.linked_memory_ids),
    )


def analyze(memories: list[MemoryRecord], incoming: list[MemoryRecord] | None = None):
    return PredictiveMemoryEngine(stale_after_days=30).analyze(
        memories,
        incoming_memories=incoming,
        as_of=AS_OF,
    )


def signal_types(result):
    return {trace.signal_type for trace in result.expectation_traces}


def candidate_signals(result):
    return {candidate.signal_type for candidate in result.prediction_candidates}


def test_predictive_memory_is_deterministic() -> None:
    memory = MemoryRecord(content="floating memory", id="mem-1")

    first = analyze([memory])
    second = analyze([memory])

    assert [trace.trace_id for trace in first.expectation_traces] == [trace.trace_id for trace in second.expectation_traces]
    assert [candidate.candidate_id for candidate in first.prediction_candidates] == [candidate.candidate_id for candidate in second.prediction_candidates]
    assert first.warnings == second.warnings


def test_missing_provenance_creates_review_expectation_not_evidence() -> None:
    memory = MemoryRecord(content="floating memory", id="mem-1")

    result = analyze([memory])

    assert PredictiveSignalType.EXPECTED_MISSING_PROVENANCE in signal_types(result)
    assert PredictiveSignalType.EXPECTED_MISSING_PROVENANCE in candidate_signals(result)
    assert PredictiveWarningType.PREDICTION_NOT_EVIDENCE in result.warnings
    assert PredictiveWarningType.EXPECTATION_NOT_TRUTH in result.warnings


def test_contradiction_pressure_predicts_review_attention() -> None:
    memory = MemoryRecord(
        content="conflicting memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.7,
        needs_review=True,
        linked_memory_ids=["mem-2"],
    )

    result = analyze([memory])

    assert PredictiveSignalType.EXPECTED_CONTRADICTION in signal_types(result)
    candidate = [item for item in result.prediction_candidates if item.target_id == "mem-1"][0]
    assert candidate.review_priority == 0.7
    assert PredictiveWarningType.SURPRISE_NOT_DISPROOF in candidate.warning_flags


def test_duplicate_memory_keys_create_lineage_echo_expectation() -> None:
    first = MemoryRecord(content="same memory", evidence_ids={"ev-1"}, id="mem-1")
    second = MemoryRecord(content=" same   memory ", evidence_ids={"ev-2"}, id="mem-2")

    result = analyze([first, second])

    assert PredictiveSignalType.EXPECTED_LINEAGE_ECHO in signal_types(result)
    assert PredictiveWarningType.RECURRENCE_NOT_CORROBORATION in result.warnings
    assert {candidate.target_id for candidate in result.prediction_candidates} >= {"mem-1", "mem-2"}


def test_stale_memory_creates_refresh_expectation_without_decay() -> None:
    memory = MemoryRecord(
        content="old memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        memory_strength=0.4,
        last_accessed_at=OLD_DATE,
    )
    before = snapshot(memory)

    result = analyze([memory])

    assert snapshot(memory) == before
    assert result.mutated_state is False
    assert PredictiveSignalType.EXPECTED_STALE_MEMORY in signal_types(result)


def test_unexpected_incoming_provenance_gap_creates_prediction_error_and_surprise() -> None:
    prior = MemoryRecord(content="stable memory", evidence_ids={"ev-1"}, id="mem-1")
    incoming = MemoryRecord(content="unexpected floating memory", id="mem-new")

    result = analyze([prior], [incoming])

    assert result.prediction_errors
    assert result.prediction_errors[0].expected_signal is PredictiveSignalType.EXPECTED_MISSING_PROVENANCE
    assert result.surprise_signals
    assert result.surprise_signals[0].target_id == "mem-new"
    assert PredictiveWarningType.SURPRISE_NOT_DISPROOF in result.warnings


def test_unexpected_incoming_contradiction_creates_surprise_not_disproof() -> None:
    prior = MemoryRecord(content="stable memory", evidence_ids={"ev-1"}, id="mem-1")
    incoming = MemoryRecord(
        content="new contradiction",
        evidence_ids={"ev-2"},
        id="mem-new",
        contradiction_pressure=0.8,
        needs_review=True,
    )

    result = analyze([prior], [incoming])

    assert any(error.expected_signal is PredictiveSignalType.EXPECTED_CONTRADICTION for error in result.prediction_errors)
    assert any(signal.reason == "unexpected contradiction pressure" for signal in result.surprise_signals)
    assert PredictiveWarningType.SURPRISE_NOT_DISPROOF in result.warnings


def test_predictive_review_adapter_returns_attention_candidates_only() -> None:
    memory = MemoryRecord(
        content="conflicting memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.6,
        needs_review=True,
    )
    result = analyze([memory])

    candidates = PredictiveReviewAdapter().to_attention_candidates(result)

    assert candidates
    assert candidates[0].record_type == "memory"
    assert candidates[0].metadata["predictive_memory_context_only"] is True
    assert candidates[0].provenance_ids == set()


def test_predictive_attention_candidates_affect_ordering_not_truth() -> None:
    contradicted = MemoryRecord(
        content="conflicting memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.8,
        needs_review=True,
    )
    stale = MemoryRecord(content="old memory", evidence_ids={"ev-2"}, id="mem-2", last_accessed_at=OLD_DATE)
    candidates = PredictiveReviewAdapter().to_attention_candidates(analyze([contradicted, stale]))

    decision = AttentionEngine().prioritize(candidates, limit=2)

    assert "mem-1" in {candidate.record_id for candidate in decision.selected_for_review}
    assert all(candidate.metadata["predictive_memory_context_only"] is True for candidate in decision.selected_records)


def test_expectation_guardrails_block_evidence_promotion() -> None:
    result = analyze([MemoryRecord(content="floating memory", id="mem-1")])
    guardrails = ExpectationGuardrails()

    assert guardrails.blocks_evidence_promotion(result) is True
    assert PredictiveWarningType.EXPECTATION_NOT_TRUTH in guardrails.warnings_for(result)
    assert PredictiveWarningType.REVIEW_ATTENTION_ONLY in guardrails.warnings_for(result)
