"""Memory decay and duplicate merge behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from roswell_uap_cortex.models import MemoryRecord


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def sync_strength(record: MemoryRecord, value: float) -> None:
    """Keep legacy strength and cognitive memory strength aligned."""
    bounded = _clamp(value)
    record.memory_strength = bounded
    record.strength = bounded


@dataclass(slots=True)
class MemoryDecayEngine:
    """Apply bounded decay and reinforcement to uncertainty-preserving memories."""

    daily_decay_rate: float = 0.03
    weak_memory_threshold: float = 0.4
    weak_memory_multiplier: float = 1.75
    duplicate_reinforcement: float = 0.08
    access_reinforcement: float = 0.02
    max_strength: float = 0.95
    archival_threshold: float = 0.2
    contradiction_decay_damping: float = 0.5

    def merge_duplicate(
        self,
        existing: MemoryRecord,
        incoming: MemoryRecord,
        *,
        merged_at: datetime | None = None,
    ) -> MemoryRecord:
        """Merge a duplicate memory into an existing record and return the existing one."""
        if existing.normalized_key != incoming.normalized_key:
            raise ValueError("Only memories with the same normalized key can merge")

        timestamp = merged_at or datetime.now(timezone.utc)
        existing.evidence_ids.update(incoming.evidence_ids)
        for tag in incoming.tags:
            if tag not in existing.tags:
                existing.tags.append(tag)
        for memory_id in incoming.linked_memory_ids:
            if memory_id not in existing.linked_memory_ids:
                existing.linked_memory_ids.append(memory_id)
        existing.access_count += incoming.access_count + 1
        existing.activation_count += incoming.activation_count
        existing.consistency_count += incoming.consistency_count
        existing.last_accessed_at = timestamp
        if incoming.last_activated_at is not None:
            existing.last_activated_at = incoming.last_activated_at
        existing.contradiction_pressure = max(
            existing.contradiction_pressure,
            incoming.contradiction_pressure,
        )
        if existing.source_confidence is None:
            existing.source_confidence = incoming.source_confidence
        elif incoming.source_confidence is not None:
            existing.source_confidence = max(existing.source_confidence, incoming.source_confidence)
        sync_strength(
            existing,
            _clamp(
                max(existing.memory_strength, incoming.memory_strength)
                + self.duplicate_reinforcement,
                upper=self.max_strength,
            ),
        )
        existing.archival = (
            existing.archival
            and incoming.archival
            and existing.memory_strength < self.archival_threshold
        )
        return existing

    def merge_all_duplicates(self, records: list[MemoryRecord]) -> list[MemoryRecord]:
        """Collapse duplicate memories by normalized content key."""
        merged: dict[str, MemoryRecord] = {}
        for record in records:
            if record.normalized_key in merged:
                self.merge_duplicate(merged[record.normalized_key], record)
            else:
                merged[record.normalized_key] = record
        return list(merged.values())

    def apply_decay(
        self,
        record: MemoryRecord,
        *,
        as_of: datetime | None = None,
    ) -> MemoryRecord:
        """Decay memories by days since activation and mark weak memories archival."""
        timestamp = as_of or datetime.now(timezone.utc)
        anchor = record.last_activated_at or record.last_accessed_at or record.created_at
        elapsed_days = max((timestamp - anchor).total_seconds() / 86400, 0.0)

        decay_rate = record.decay_rate or self.daily_decay_rate
        if record.memory_strength < self.weak_memory_threshold and record.activation_count == 0:
            decay_rate *= self.weak_memory_multiplier
        if record.contradiction_pressure > 0:
            decay_rate *= 1 - min(record.contradiction_pressure, 1.0) * self.contradiction_decay_damping

        decay_amount = elapsed_days * decay_rate
        reinforcement = min(record.activation_count, 5) * self.access_reinforcement
        sync_strength(record, record.memory_strength - decay_amount + reinforcement)

        if record.memory_strength < self.archival_threshold:
            record.archival = True
        return record
