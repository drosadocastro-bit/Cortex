from datetime import datetime, timezone

import pytest

from roswell_uap_cortex import (
    ContradictionPressureEngine,
    MemoryActivationEngine,
    MemoryDecayEngine,
    MemoryRecord,
    SemanticCompressionEngine,
)


def test_duplicate_memories_merge_instead_of_accumulating() -> None:
    engine = MemoryDecayEngine()
    first = MemoryRecord(
        content="Witness reported a bright object near the horizon",
        evidence_ids={"evidence-1"},
        strength=0.45,
    )
    duplicate = MemoryRecord(
        content="  witness   reported a bright object near the horizon  ",
        evidence_ids={"evidence-2"},
        strength=0.5,
    )

    merged = engine.merge_all_duplicates([first, duplicate])

    assert len(merged) == 1
    assert merged[0] is first
    assert merged[0].evidence_ids == {"evidence-1", "evidence-2"}
    assert merged[0].consistency_count == 2
    assert merged[0].access_count == 1
    assert merged[0].memory_strength > duplicate.memory_strength


def test_non_duplicate_memories_remain_separate() -> None:
    engine = MemoryDecayEngine()
    records = [
        MemoryRecord(content="A document mentions a radar contact"),
        MemoryRecord(content="A witness describes a recovered material"),
    ]

    merged = engine.merge_all_duplicates(records)

    assert len(merged) == 2


def test_merge_rejects_different_normalized_keys() -> None:
    engine = MemoryDecayEngine()
    first = MemoryRecord(content="first memory")
    second = MemoryRecord(content="second memory")

    with pytest.raises(ValueError):
        engine.merge_duplicate(first, second)


def test_decay_reduces_weak_unused_memory() -> None:
    engine = MemoryDecayEngine(daily_decay_rate=0.05)
    record = MemoryRecord(
        content="weak unused memory",
        memory_strength=0.3,
        last_accessed_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )

    decayed = engine.apply_decay(
        record,
        as_of=datetime(2026, 5, 11, tzinfo=timezone.utc),
    )

    assert decayed.memory_strength < 0.3


def test_repeated_consistent_memory_reinforces_with_cap() -> None:
    engine = MemoryDecayEngine(max_strength=0.6, duplicate_reinforcement=0.2)
    first = MemoryRecord(content="consistent memory", memory_strength=0.55)
    duplicate = MemoryRecord(content="consistent memory", memory_strength=0.58)

    merged = engine.merge_duplicate(first, duplicate)

    assert merged.consistency_count == 2
    assert merged.memory_strength == 0.6


def test_repeated_activation_increases_strength_but_caps_at_one() -> None:
    engine = MemoryActivationEngine(reinforcement=0.3)
    record = MemoryRecord(content="activated memory", memory_strength=0.5)

    engine.activate(record, datetime(2026, 5, 1, tzinfo=timezone.utc))
    engine.activate(record, datetime(2026, 5, 2, tzinfo=timezone.utc))

    assert record.activation_count == 2
    assert record.memory_strength == 1.0
    assert record.strength == 1.0


def test_unused_memories_decay_over_time() -> None:
    engine = MemoryDecayEngine()
    record = MemoryRecord(
        content="unused memory",
        memory_strength=0.8,
        last_activated_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )

    engine.apply_decay(record, as_of=datetime(2026, 5, 11, tzinfo=timezone.utc))

    assert record.memory_strength < 0.8


def test_weak_unused_memories_become_archival_instead_of_deleted() -> None:
    engine = MemoryDecayEngine(archival_threshold=0.2)
    record = MemoryRecord(
        content="fading memory",
        memory_strength=0.21,
        last_activated_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )

    decayed = engine.apply_decay(
        record,
        as_of=datetime(2026, 5, 10, tzinfo=timezone.utc),
    )

    assert decayed is record
    assert record.archival is True


def test_archival_memory_can_reactivate_when_sufficiently_reinforced() -> None:
    engine = MemoryActivationEngine(reinforcement=0.4, archival_reactivation_threshold=0.55)
    record = MemoryRecord(
        content="archived but relevant memory",
        memory_strength=0.2,
        archival=True,
    )

    engine.activate(record, datetime(2026, 5, 1, tzinfo=timezone.utc))

    assert record.archival is False
    assert record.memory_strength == pytest.approx(0.6)


def test_semantic_compression_preserves_ids_activation_counts_and_source_confidence() -> None:
    engine = SemanticCompressionEngine()
    first = MemoryRecord(
        content="radar sighting report",
        memory_strength=0.7,
        activation_count=2,
        contradiction_pressure=0.2,
        tags=["radar", "timeline"],
        source_confidence=0.6,
    )
    second = MemoryRecord(
        content="radar sighting note",
        memory_strength=0.6,
        activation_count=3,
        contradiction_pressure=0.4,
        tags=["radar", "source"],
        source_confidence=0.8,
    )

    compressed = engine.compress([first, second], canonical_topic="radar sighting")

    assert compressed.merged_memory_ids == [first.id, second.id]
    assert compressed.activation_count == 5
    assert compressed.average_contradiction_pressure == pytest.approx(0.3)
    assert compressed.highest_source_confidence == 0.8
    assert compressed.strongest_tags[0] == "radar"


def test_contradictions_increase_pressure_without_deleting_memories() -> None:
    engine = ContradictionPressureEngine(pressure_increment=0.25)
    first = MemoryRecord(content="claim says event happened before midnight")
    second = MemoryRecord(content="claim says event happened after midnight")

    updated_first, updated_second = engine.register_conflict(first, second)

    assert updated_first is first
    assert updated_second is second
    assert first.contradiction_pressure == 0.25
    assert second.contradiction_pressure == 0.25
    assert second.id in first.linked_memory_ids
    assert first.id in second.linked_memory_ids
    assert first.needs_review is True
    assert second.uncertainty_preserved is True


def test_memory_strength_never_exceeds_one_or_drops_below_zero() -> None:
    activation = MemoryActivationEngine(reinforcement=5.0)
    decay = MemoryDecayEngine(daily_decay_rate=1.0)
    record = MemoryRecord(
        content="bounded memory",
        memory_strength=0.9,
        last_activated_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )

    activation.activate(record, datetime(2026, 5, 2, tzinfo=timezone.utc))
    assert record.memory_strength == 1.0

    decay.apply_decay(record, as_of=datetime(2026, 6, 30, tzinfo=timezone.utc))
    assert record.memory_strength == 0.0
