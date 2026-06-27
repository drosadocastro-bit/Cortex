from datetime import datetime, timezone

from roswell_uap_cortex import (
    DreamRecommendationType,
    DreamReplayEngine,
    DreamReplayRequest,
    DreamWarningType,
    MemoryDecayEngine,
    MemoryRecord,
)


AS_OF = datetime(2026, 6, 27, tzinfo=timezone.utc)
OLD_DATE = datetime(2026, 5, 1, tzinfo=timezone.utc)


def snapshot(memory: MemoryRecord) -> tuple[object, ...]:
    return (
        memory.id,
        memory.memory_strength,
        memory.strength,
        memory.archival,
        memory.access_count,
        memory.activation_count,
        memory.consistency_count,
        memory.last_accessed_at,
        memory.last_activated_at,
        memory.contradiction_pressure,
        memory.needs_review,
        memory.uncertainty_preserved,
        tuple(sorted(memory.evidence_ids)),
        tuple(memory.linked_memory_ids),
    )


def replay(memories: list[MemoryRecord]):
    return DreamReplayEngine().replay(
        DreamReplayRequest(memory_records=memories, as_of=AS_OF, stale_after_days=30)
    )


def test_dream_replay_is_deterministic() -> None:
    first = MemoryRecord(content="radar memory", evidence_ids={"ev-1"}, id="mem-1")
    second = MemoryRecord(content="archival memory", evidence_ids={"ev-2"}, id="mem-2", archival=True)

    one = replay([second, first])
    two = replay([second, first])

    assert one.request_id == two.request_id
    assert one.artifact.artifact_id == two.artifact.artifact_id
    assert [note.note_id for note in one.consolidation_notes] == [note.note_id for note in two.consolidation_notes]
    assert [rec.recommendation_id for rec in one.recommendations] == [rec.recommendation_id for rec in two.recommendations]


def test_dream_replay_does_not_apply_decay_or_mutate_memory() -> None:
    memory = MemoryRecord(
        content="weak stale memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        memory_strength=0.25,
        last_accessed_at=OLD_DATE,
    )
    before = snapshot(memory)

    result = replay([memory])

    assert snapshot(memory) == before
    assert result.mutated_state is False
    assert memory.archival is False
    assert any(rec.recommendation_type == DreamRecommendationType.CONSIDER_ARCHIVAL for rec in result.recommendations)


def test_dream_replay_duplicate_candidates_do_not_merge_memories() -> None:
    first = MemoryRecord(content="same memory", evidence_ids={"ev-1"}, id="mem-1")
    duplicate = MemoryRecord(content="  same   memory ", evidence_ids={"ev-2"}, id="mem-2")

    result = replay([first, duplicate])

    assert result.duplicate_candidate_groups == [["mem-1", "mem-2"]]
    assert first.evidence_ids == {"ev-1"}
    assert duplicate.evidence_ids == {"ev-2"}
    assert any(rec.recommendation_type == DreamRecommendationType.REVIEW_DUPLICATE for rec in result.recommendations)
    assert DreamWarningType.DUPLICATE_NOT_CORROBORATION in result.warnings


def test_dream_replay_preserves_contradiction_visibility_without_resolution() -> None:
    first = MemoryRecord(
        content="event before midnight",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=0.4,
        linked_memory_ids=["mem-2"],
        needs_review=True,
        uncertainty_preserved=True,
    )
    second = MemoryRecord(content="event after midnight", evidence_ids={"ev-2"}, id="mem-2")

    result = replay([first, second])

    assert result.contradiction_memory_ids == {"mem-1"}
    assert any(note.note_type == "contradiction_pressure" for note in result.consolidation_notes)
    assert any(rec.recommendation_type == DreamRecommendationType.REVIEW_CONTRADICTION for rec in result.recommendations)
    assert any(rec.recommendation_type == DreamRecommendationType.PRESERVE_UNCERTAINTY for rec in result.recommendations)
    assert DreamWarningType.CONTRADICTION_NOT_RESOLUTION in result.warnings
    assert first.needs_review is True


def test_dream_replay_archival_memory_remains_archival() -> None:
    memory = MemoryRecord(
        content="archival memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        archival=True,
        memory_strength=0.2,
    )

    result = replay([memory])

    assert result.archival_memory_ids == {"mem-1"}
    assert memory.archival is True
    assert any(note.note_type == "archival_preserved" for note in result.consolidation_notes)


def test_dream_replay_missing_evidence_remains_visible() -> None:
    memory = MemoryRecord(content="floating memory", id="mem-1")

    result = replay([memory])

    assert any(note.note_type == "missing_evidence_reference" for note in result.consolidation_notes)
    assert DreamWarningType.MISSING_PROVENANCE_VISIBLE in result.warnings


def test_dream_replay_recommendation_priorities_are_bounded() -> None:
    memory = MemoryRecord(
        content="high pressure memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        contradiction_pressure=5.0,
        needs_review=True,
    )

    result = replay([memory])

    assert result.recommendations
    assert all(0.0 <= rec.priority <= 1.0 for rec in result.recommendations)


def test_existing_decay_engine_still_applies_decay_separately() -> None:
    memory = MemoryRecord(
        content="weak stale memory",
        evidence_ids={"ev-1"},
        id="mem-1",
        memory_strength=0.25,
        last_accessed_at=OLD_DATE,
    )

    replay([memory])
    DreamReplayEngine().replay(DreamReplayRequest(memory_records=[memory], as_of=AS_OF))
    strength_after_dreams = memory.memory_strength

    MemoryDecayEngine(daily_decay_rate=0.05).apply_decay(memory, as_of=AS_OF)

    assert strength_after_dreams == 0.25
    assert memory.memory_strength < strength_after_dreams
