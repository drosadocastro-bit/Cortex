"""Contradiction pressure behavior for uncertain memories."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import MemoryRecord


@dataclass(slots=True)
class ContradictionPressureEngine:
    """Preserve conflicting memories while increasing review pressure."""

    pressure_increment: float = 0.2

    def register_conflict(
        self,
        first: MemoryRecord,
        second: MemoryRecord,
        *,
        pressure: float | None = None,
    ) -> tuple[MemoryRecord, MemoryRecord]:
        increment = self.pressure_increment if pressure is None else pressure

        first.contradiction_pressure = _clamp(first.contradiction_pressure + increment)
        second.contradiction_pressure = _clamp(second.contradiction_pressure + increment)

        if second.id not in first.linked_memory_ids:
            first.linked_memory_ids.append(second.id)
        if first.id not in second.linked_memory_ids:
            second.linked_memory_ids.append(first.id)

        first.needs_review = True
        second.needs_review = True
        first.uncertainty_preserved = True
        second.uncertainty_preserved = True
        return first, second
