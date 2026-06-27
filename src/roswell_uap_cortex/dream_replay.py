"""Offline memory consolidation and dream replay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.models import (
    ConsolidationRecommendation,
    DreamArtifact,
    DreamRecommendationType,
    DreamReplayRequest,
    DreamReplayResult,
    DreamWarningType,
    MemoryConsolidationNote,
    MemoryRecord,
)


@dataclass(slots=True)
class DreamReplayEngine:
    """Inspect existing memories during offline rest and emit review recommendations.

    Dream replay is deliberately read-only. It does not apply decay, merge
    duplicate memories, reactivate archival memories, create evidence, create
    graph edges, or upgrade associations into confirmation.
    """

    low_strength_threshold: float = 0.3
    high_contradiction_threshold: float = 0.2
    default_stale_after_days: int = 30

    def replay(self, request: DreamReplayRequest) -> DreamReplayResult:
        as_of = request.as_of or datetime.now(timezone.utc)
        stale_after_days = request.stale_after_days or self.default_stale_after_days
        input_fingerprint = self._fingerprint(request.memory_records)

        memories = sorted(
            [memory for memory in request.memory_records if request.include_archival or not memory.archival],
            key=lambda memory: (memory.normalized_key or MemoryRecord.content_key(memory.content), memory.id),
        )

        notes: list[MemoryConsolidationNote] = []
        recommendations: list[ConsolidationRecommendation] = []
        stale_ids: set[str] = set()
        archival_ids: set[str] = set()
        contradiction_ids: set[str] = set()

        duplicate_groups = self._duplicate_groups(memories)
        for group in duplicate_groups:
            recommendations.append(
                ConsolidationRecommendation(
                    recommendation_type=DreamRecommendationType.REVIEW_DUPLICATE,
                    memory_ids=set(group),
                    rationale="Duplicate memory candidates should be reviewed by the existing merge path.",
                    priority=0.65,
                )
            )
            for memory_id in group:
                notes.append(
                    MemoryConsolidationNote(
                        memory_id=memory_id,
                        note_type="duplicate_candidate",
                        message="Dream replay found duplicate-key memory candidates; this is not corroboration.",
                        related_memory_ids=set(group) - {memory_id},
                    )
                )

        for memory in memories:
            memory_notes, memory_recommendations = self._inspect_memory(
                memory,
                as_of=as_of,
                stale_after_days=stale_after_days,
            )
            notes.extend(memory_notes)
            recommendations.extend(memory_recommendations)

            if self._is_stale(memory, as_of=as_of, stale_after_days=stale_after_days):
                stale_ids.add(memory.id)
            if memory.archival:
                archival_ids.add(memory.id)
            if memory.contradiction_pressure >= self.high_contradiction_threshold or memory.needs_review:
                contradiction_ids.add(memory.id)

        recommendations = self._deduplicate_recommendations(recommendations)
        notes = sorted(notes, key=lambda note: (note.memory_id, note.note_type, note.note_id))
        replayed_ids = [memory.id for memory in memories]
        artifact_id = str(uuid5(NAMESPACE_URL, f"dream-artifact:{request.request_id}:{':'.join(replayed_ids)}"))
        limitations = [
            "Dream replay is an internal consolidation artifact, not evidence.",
            "Recommendations require an explicit downstream action before any memory state changes.",
            "Duplicate replay is not independent corroboration.",
        ]
        warnings = [
            DreamWarningType.DREAM_NOT_EVIDENCE,
            DreamWarningType.REPLAY_NOT_CONFIRMATION,
            DreamWarningType.DUPLICATE_NOT_CORROBORATION,
            DreamWarningType.CONTRADICTION_NOT_RESOLUTION,
            DreamWarningType.RECOMMENDATION_NOT_MUTATION,
        ]
        if any(not memory.evidence_ids for memory in memories):
            warnings.append(DreamWarningType.MISSING_PROVENANCE_VISIBLE)

        output_fingerprint = self._fingerprint(request.memory_records)

        return DreamReplayResult(
            request_id=request.request_id,
            artifact=DreamArtifact(
                artifact_id=artifact_id,
                source_memory_ids=set(replayed_ids),
                generated_at=as_of,
                notes=["Offline memory replay completed without applying memory changes."],
                limitations=limitations.copy(),
            ),
            consolidation_notes=notes,
            recommendations=recommendations,
            replayed_memory_ids=replayed_ids,
            duplicate_candidate_groups=duplicate_groups,
            contradiction_memory_ids=contradiction_ids,
            stale_memory_ids=stale_ids,
            archival_memory_ids=archival_ids,
            warnings=warnings,
            limitations=limitations,
            mutated_state=input_fingerprint != output_fingerprint,
        )

    def _inspect_memory(
        self,
        memory: MemoryRecord,
        *,
        as_of: datetime,
        stale_after_days: int,
    ) -> tuple[list[MemoryConsolidationNote], list[ConsolidationRecommendation]]:
        notes: list[MemoryConsolidationNote] = []
        recommendations: list[ConsolidationRecommendation] = []

        if memory.contradiction_pressure >= self.high_contradiction_threshold or memory.needs_review:
            notes.append(
                MemoryConsolidationNote(
                    memory_id=memory.id,
                    note_type="contradiction_pressure",
                    message="Memory carries unresolved contradiction or review pressure.",
                    related_memory_ids=set(memory.linked_memory_ids),
                    evidence_ids=set(memory.evidence_ids),
                )
            )
            recommendations.append(
                ConsolidationRecommendation(
                    recommendation_type=DreamRecommendationType.REVIEW_CONTRADICTION,
                    memory_ids={memory.id, *memory.linked_memory_ids},
                    rationale="Preserve contradiction visibility during the next review cycle.",
                    priority=max(0.6, min(1.0, memory.contradiction_pressure)),
                )
            )

        if self._is_stale(memory, as_of=as_of, stale_after_days=stale_after_days):
            notes.append(
                MemoryConsolidationNote(
                    memory_id=memory.id,
                    note_type="stale_memory",
                    message="Memory has not been activated within the stale replay window.",
                    evidence_ids=set(memory.evidence_ids),
                )
            )
            if memory.memory_strength <= self.low_strength_threshold:
                recommendations.append(
                    ConsolidationRecommendation(
                        recommendation_type=DreamRecommendationType.CONSIDER_ARCHIVAL,
                        memory_ids={memory.id},
                        rationale="Weak stale memory may be suitable for archival review, not deletion.",
                        priority=0.45,
                    )
                )
            else:
                recommendations.append(
                    ConsolidationRecommendation(
                        recommendation_type=DreamRecommendationType.REFRESH_ATTENTION,
                        memory_ids={memory.id},
                        rationale="Stale but still strong memory may deserve focused review replay.",
                        priority=0.5,
                    )
                )

        if memory.archival:
            notes.append(
                MemoryConsolidationNote(
                    memory_id=memory.id,
                    note_type="archival_preserved",
                    message="Archival memory remains available; dream replay does not reactivate it.",
                    evidence_ids=set(memory.evidence_ids),
                )
            )

        if memory.uncertainty_preserved:
            recommendations.append(
                ConsolidationRecommendation(
                    recommendation_type=DreamRecommendationType.PRESERVE_UNCERTAINTY,
                    memory_ids={memory.id},
                    rationale="Memory already carries explicit uncertainty that should remain visible.",
                    priority=0.55,
                )
            )

        if not memory.evidence_ids:
            notes.append(
                MemoryConsolidationNote(
                    memory_id=memory.id,
                    note_type="missing_evidence_reference",
                    message="Memory has no evidence ids attached; provenance gap remains visible.",
                )
            )

        return notes, recommendations

    def _duplicate_groups(self, memories: list[MemoryRecord]) -> list[list[str]]:
        by_key: dict[str, list[str]] = {}
        for memory in memories:
            key = memory.normalized_key or MemoryRecord.content_key(memory.content)
            by_key.setdefault(key, []).append(memory.id)
        return [sorted(ids) for _key, ids in sorted(by_key.items()) if len(ids) > 1]

    def _is_stale(self, memory: MemoryRecord, *, as_of: datetime, stale_after_days: int) -> bool:
        anchor = memory.last_activated_at or memory.last_accessed_at or memory.created_at
        return (as_of - anchor).total_seconds() / 86400 >= stale_after_days

    def _deduplicate_recommendations(
        self,
        recommendations: list[ConsolidationRecommendation],
    ) -> list[ConsolidationRecommendation]:
        by_key: dict[tuple[str, tuple[str, ...], str], ConsolidationRecommendation] = {}
        for recommendation in recommendations:
            key = (
                recommendation.recommendation_type.value,
                tuple(sorted(recommendation.memory_ids)),
                recommendation.rationale,
            )
            existing = by_key.get(key)
            if existing is None or recommendation.priority > existing.priority:
                by_key[key] = recommendation
        return sorted(
            by_key.values(),
            key=lambda rec: (-rec.priority, rec.recommendation_type.value, sorted(rec.memory_ids)),
        )

    def _fingerprint(self, memories: list[MemoryRecord]) -> tuple[tuple[object, ...], ...]:
        return tuple(
            sorted(
                (
                    memory.id,
                    memory.normalized_key,
                    memory.memory_strength,
                    memory.strength,
                    memory.archival,
                    memory.access_count,
                    memory.activation_count,
                    memory.consistency_count,
                    memory.last_accessed_at.isoformat(),
                    memory.last_activated_at.isoformat() if memory.last_activated_at else None,
                    memory.contradiction_pressure,
                    memory.needs_review,
                    memory.uncertainty_preserved,
                    tuple(sorted(memory.evidence_ids)),
                    tuple(memory.tags),
                    tuple(memory.linked_memory_ids),
                )
                for memory in memories
            )
        )
