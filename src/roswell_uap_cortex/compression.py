"""Deterministic semantic compression for related memories."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from roswell_uap_cortex.models import MemoryRecord


@dataclass(slots=True)
class CompressedMemory:
    """A deterministic summary of near-duplicate or topic-equivalent memories."""

    summary: str
    canonical_topic: str
    merged_memory_ids: list[str]
    strongest_tags: list[str]
    activation_count: int
    average_contradiction_pressure: float
    highest_source_confidence: float | None = None
    source_memory_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticCompressionEngine:
    """Compress related memories without using an LLM or vector database."""

    max_tags: int = 5

    def compress(
        self,
        memories: list[MemoryRecord],
        *,
        canonical_topic: str | None = None,
    ) -> CompressedMemory:
        if not memories:
            raise ValueError("Cannot compress an empty memory set")

        topic = canonical_topic or memories[0].normalized_key or MemoryRecord.content_key(memories[0].content)
        merged_ids = [memory.id for memory in memories]
        activation_total = sum(memory.activation_count for memory in memories)
        average_pressure = sum(memory.contradiction_pressure for memory in memories) / len(memories)
        source_confidences = [
            memory.source_confidence
            for memory in memories
            if memory.source_confidence is not None
        ]

        tag_counts: Counter[str] = Counter()
        for memory in memories:
            for tag in memory.tags:
                tag_counts[tag] += max(memory.activation_count, 1)

        strongest_tags = [
            tag
            for tag, _count in sorted(
                tag_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[: self.max_tags]
        ]

        return CompressedMemory(
            summary=f"Compressed memory for topic: {topic}",
            canonical_topic=topic,
            merged_memory_ids=merged_ids,
            source_memory_ids=merged_ids.copy(),
            strongest_tags=strongest_tags,
            activation_count=activation_total,
            average_contradiction_pressure=average_pressure,
            highest_source_confidence=max(source_confidences) if source_confidences else None,
        )
