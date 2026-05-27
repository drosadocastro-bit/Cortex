"""Associative memory activation behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from roswell_uap_cortex.memory import _clamp, sync_strength
from roswell_uap_cortex.models import MemoryRecord


@dataclass(slots=True)
class MemoryActivationEngine:
    """Reinforce memories when attention activates them."""

    reinforcement: float = 0.12
    archival_reactivation_threshold: float = 0.55

    def activate(
        self,
        memory: MemoryRecord,
        activated_at: datetime | None = None,
        *,
        reinforcement: float | None = None,
    ) -> MemoryRecord:
        timestamp = activated_at or datetime.now(timezone.utc)
        boost = self.reinforcement if reinforcement is None else reinforcement

        memory.activation_count += 1
        memory.access_count += 1
        memory.last_activated_at = timestamp
        memory.last_accessed_at = timestamp
        sync_strength(memory, _clamp(memory.memory_strength + boost))

        if memory.archival and memory.memory_strength >= self.archival_reactivation_threshold:
            memory.archival = False

        return memory
