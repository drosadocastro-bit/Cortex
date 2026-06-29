from datetime import datetime, timezone

from roswell_uap_cortex import (
    AttentionEngine,
    DreamBoundaryGuardrails,
    DreamInfluencePolicy,
    DreamRecommendationType,
    DreamReplayEngine,
    DreamReplayRequest,
    DreamReviewAdapter,
    MemoryRecord,
    ReviewInfluenceScope,
    ReviewInfluenceWarningType,
)


AS_OF = datetime(2026, 6, 29, tzinfo=timezone.utc)
OLD_DATE = datetime(2026, 5, 1, tzinfo=timezone.utc)


def replay(memories: list[MemoryRecord]):
    return DreamReplayEngine().replay(
        DreamReplayRequest(memory_records=memories, as_of=AS_OF, stale_after_days=30)
    )


def snapshot(memory: MemoryRecord) -> tuple[object, ...]:
    return (
        memory.memory_strength,
        memory.strength,
        memory.archival,
        memory.access_count,
        memory.activation_count,
        memory.consistency_count,
        memory.contradiction_pressure,
        memory.needs_review,
        tuple(sorted(memory.evidence_ids)),
        tuple(memory.linked_memory_ids),
    )


def warning_types(influence):
    return {warning.warning_type for warning in influence.warnings}


def test_dream_influence_maps_recommendations_to_review_signals_only() -> None:
    memory = MemoryRecord(
        content="event before midnight",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.6,
        linked_memory_ids=["mem-2"],
        needs_review=True,
        uncertainty_preserved=True,
    )
    result = replay([memory])

    influence = DreamInfluencePolicy().evaluate(result)

    assert "mem-1" in influence.prioritized_ids
    assert "mem-1" in influence.must_include_ids
    assert "mem-1" in influence.contradiction_ids
    assert all(ReviewInfluenceScope.ATTENTION in signal.allowed_scopes for signal in influence.signals)
    assert any(signal.signal_type.startswith("dream:") for signal in influence.signals)
    assert ReviewInfluenceWarningType.DREAM_NOT_EVIDENCE in warning_types(influence)
    assert ReviewInfluenceWarningType.DREAM_REPLAY_NOT_CONFIRMATION in warning_types(influence)


def test_dream_influence_does_not_mutate_memory_or_apply_recommendations() -> None:
    memory = MemoryRecord(
        content="weak stale memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        memory_strength=0.25,
        last_accessed_at=OLD_DATE,
    )
    before = snapshot(memory)

    result = replay([memory])
    influence = DreamInfluencePolicy().evaluate(result)

    assert snapshot(memory) == before
    assert result.mutated_state is False
    assert memory.archival is False
    assert "mem-1" in influence.deferred_ids
    assert any(
        recommendation.recommendation_type is DreamRecommendationType.CONSIDER_ARCHIVAL
        for recommendation in result.recommendations
    )


def test_duplicate_dream_candidates_do_not_become_corroboration() -> None:
    first = MemoryRecord(content="same memory", evidence_ids={"ev-1"}, id="mem-1")
    duplicate = MemoryRecord(content=" same   memory ", evidence_ids={"ev-2"}, id="mem-2")

    result = replay([first, duplicate])
    influence = DreamInfluencePolicy().evaluate(result)

    assert result.duplicate_candidate_groups == [["mem-1", "mem-2"]]
    assert first.evidence_ids == {"ev-1"}
    assert duplicate.evidence_ids == {"ev-2"}
    assert ReviewInfluenceWarningType.DREAM_DUPLICATE_NOT_CORROBORATION in warning_types(influence)


def test_dream_contradictions_remain_unresolved_review_context() -> None:
    first = MemoryRecord(
        content="event before midnight",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.4,
        linked_memory_ids=["mem-2"],
        needs_review=True,
    )
    second = MemoryRecord(content="event after midnight", evidence_ids={"ev-2"}, id="mem-2")

    influence = DreamInfluencePolicy().evaluate(replay([first, second]))

    assert "mem-1" in influence.contradiction_ids
    assert "mem-1" in influence.unresolved_ids
    assert first.needs_review is True
    assert ReviewInfluenceWarningType.DREAM_CONTRADICTION_NOT_RESOLUTION in warning_types(influence)


def test_dream_review_adapter_returns_attention_candidates_not_evidence() -> None:
    memory = MemoryRecord(
        content="contradicted memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.5,
        needs_review=True,
    )
    result = replay([memory])

    candidates = DreamReviewAdapter().to_attention_candidates(result)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.record_id == "mem-1"
    assert candidate.record_type == "memory"
    assert candidate.contested is True
    assert candidate.metadata["dream_review_context_only"] is True
    assert candidate.provenance_ids == set()


def test_dream_attention_candidates_can_affect_ordering_not_truth() -> None:
    stale = MemoryRecord(content="stale", evidence_ids={"ev-1"}, id="mem-stale", last_accessed_at=OLD_DATE)
    contradicted = MemoryRecord(
        content="contradicted",
        evidence_ids={"ev-2"},
        id="mem-contradicted",
        contradiction_pressure=0.7,
        needs_review=True,
    )
    result = replay([stale, contradicted])
    candidates = DreamReviewAdapter().to_attention_candidates(result)

    decision = AttentionEngine().prioritize(candidates, limit=2)

    assert decision.selected_for_review
    assert "mem-contradicted" in {candidate.record_id for candidate in decision.selected_for_review}
    assert all(candidate.record_type == "memory" for candidate in decision.selected_records)
    assert all(candidate.metadata["dream_review_context_only"] is True for candidate in decision.selected_records)


def test_boundary_guardrails_block_evidence_promotion() -> None:
    result = replay([MemoryRecord(content="floating memory", id="mem-1")])
    guardrails = DreamBoundaryGuardrails()

    assert guardrails.blocks_evidence_promotion(result) is True
    warnings = guardrails.warnings_for(result)

    assert ReviewInfluenceWarningType.DREAM_NOT_EVIDENCE in {warning.warning_type for warning in warnings}
    assert ReviewInfluenceWarningType.PROVENANCE_GAP_VISIBLE in {warning.warning_type for warning in warnings}


def test_repeated_dream_replay_does_not_increase_priority_or_strength() -> None:
    memory = MemoryRecord(
        content="weak stale memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        memory_strength=0.25,
        last_accessed_at=OLD_DATE,
    )

    first = DreamInfluencePolicy().evaluate(replay([memory]))
    second = DreamInfluencePolicy().evaluate(replay([memory]))

    assert snapshot(memory)[0] == 0.25
    first_priorities = [(signal.item_id, signal.priority) for signal in first.signals]
    second_priorities = [(signal.item_id, signal.priority) for signal in second.signals]
    assert first_priorities == second_priorities
