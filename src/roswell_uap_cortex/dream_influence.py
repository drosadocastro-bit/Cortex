"""Bounded review influence from dream replay artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    AttentionCandidate,
    DreamRecommendationType,
    DreamReplayResult,
    DreamWarningType,
    ReviewInfluenceResult,
    ReviewInfluenceScope,
    ReviewInfluenceWarning,
    ReviewInfluenceWarningType,
    ReviewStateSignal,
)


@dataclass(slots=True)
class DreamBoundaryGuardrails:
    """Guardrails that keep dream replay from becoming evidence or truth."""

    def warnings_for(self, result: DreamReplayResult) -> list[ReviewInfluenceWarning]:
        warnings = [
            ReviewInfluenceWarning(
                ReviewInfluenceWarningType.DREAM_NOT_EVIDENCE,
                "dream replay artifacts are internal review context, not evidence",
                {result.artifact.artifact_id},
            ),
            ReviewInfluenceWarning(
                ReviewInfluenceWarningType.DREAM_REPLAY_NOT_CONFIRMATION,
                "replayed memories and repeated replay do not confirm claims or strengthen truth",
                set(result.replayed_memory_ids),
            ),
            ReviewInfluenceWarning(
                ReviewInfluenceWarningType.DREAM_RECOMMENDATION_NOT_MUTATION,
                "dream recommendations may guide review visibility only and must not mutate records",
                self._recommended_ids(result),
            ),
        ]
        if result.duplicate_candidate_groups:
            warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.DREAM_DUPLICATE_NOT_CORROBORATION,
                    "dream duplicate candidates are merge-review hints, not independent corroboration",
                    {memory_id for group in result.duplicate_candidate_groups for memory_id in group},
                )
            )
        if result.contradiction_memory_ids:
            warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.DREAM_CONTRADICTION_NOT_RESOLUTION,
                    "dream contradiction visibility does not resolve contradictions",
                    set(result.contradiction_memory_ids),
                )
            )
        if DreamWarningType.MISSING_PROVENANCE_VISIBLE in result.warnings:
            warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.PROVENANCE_GAP_VISIBLE,
                    "dream replay preserves missing evidence references as provenance gaps",
                    {note.memory_id for note in result.consolidation_notes if note.note_type == "missing_evidence_reference"},
                )
            )
        return sorted(warnings, key=lambda warning: (warning.warning_type.value, sorted(warning.related_ids)))

    def blocks_evidence_promotion(self, result: DreamReplayResult) -> bool:
        """Dream artifacts cannot be promoted into evidence automatically."""
        return bool(result.artifact.artifact_id)

    def _recommended_ids(self, result: DreamReplayResult) -> set[str]:
        return {memory_id for recommendation in result.recommendations for memory_id in recommendation.memory_ids}


@dataclass(slots=True)
class DreamInfluencePolicy:
    """Convert dream replay output into read-only review influence."""

    guardrails: DreamBoundaryGuardrails = field(default_factory=DreamBoundaryGuardrails)

    def evaluate(self, result: DreamReplayResult) -> ReviewInfluenceResult:
        influence = ReviewInfluenceResult()
        influence.discourse_annotations.append(
            f"dream artifact {result.artifact.artifact_id} is internal review context only"
        )
        influence.uncertainty_notes.extend(result.limitations)

        for recommendation in sorted(
            result.recommendations,
            key=lambda item: (item.recommendation_type.value, sorted(item.memory_ids), item.recommendation_id),
        ):
            signal_type = f"dream:{recommendation.recommendation_type.value}"
            for memory_id in sorted(recommendation.memory_ids):
                influence.signals.append(
                    ReviewStateSignal(
                        signal_type=signal_type,
                        item_id=memory_id,
                        item_type="memory",
                        allowed_scopes={
                            ReviewInfluenceScope.ATTENTION,
                            ReviewInfluenceScope.CONTEXT,
                            ReviewInfluenceScope.DISCOURSE,
                        },
                        priority=recommendation.priority,
                        notes=[recommendation.rationale, "dream recommendation is not mutation"],
                    )
                )
                influence.prioritized_ids.add(memory_id)
                self._classify_recommendation(recommendation.recommendation_type, memory_id, influence)

        for note in sorted(result.consolidation_notes, key=lambda item: (item.memory_id, item.note_type, item.note_id)):
            if note.note_type == "missing_evidence_reference":
                influence.provenance_gap_ids.add(note.memory_id)
            if note.note_type in {"contradiction_pressure", "archival_preserved", "stale_memory"}:
                influence.unresolved_ids.add(note.memory_id)
            influence.uncertainty_notes.append(f"dream note for {note.memory_id}: {note.message}")

        influence.deferred_ids.update(result.archival_memory_ids)
        influence.unresolved_ids.update(result.stale_memory_ids | result.archival_memory_ids | result.contradiction_memory_ids)
        influence.contradiction_ids.update(result.contradiction_memory_ids)
        influence.must_include_ids.update(result.contradiction_memory_ids)
        influence.warnings.extend(self.guardrails.warnings_for(result))
        self._dedupe(influence)
        return influence

    def _classify_recommendation(
        self,
        recommendation_type: DreamRecommendationType,
        memory_id: str,
        influence: ReviewInfluenceResult,
    ) -> None:
        if recommendation_type is DreamRecommendationType.REVIEW_CONTRADICTION:
            influence.contradiction_ids.add(memory_id)
            influence.unresolved_ids.add(memory_id)
            influence.must_include_ids.add(memory_id)
        elif recommendation_type is DreamRecommendationType.REVIEW_DUPLICATE:
            influence.unresolved_ids.add(memory_id)
        elif recommendation_type is DreamRecommendationType.CONSIDER_ARCHIVAL:
            influence.deferred_ids.add(memory_id)
            influence.unresolved_ids.add(memory_id)
        elif recommendation_type is DreamRecommendationType.PRESERVE_UNCERTAINTY:
            influence.unresolved_ids.add(memory_id)
            influence.must_include_ids.add(memory_id)
        elif recommendation_type is DreamRecommendationType.REFRESH_ATTENTION:
            influence.prioritized_ids.add(memory_id)
        elif recommendation_type is DreamRecommendationType.REPLAY_FOR_REVIEW:
            influence.must_include_ids.add(memory_id)

    def _dedupe(self, influence: ReviewInfluenceResult) -> None:
        influence.uncertainty_notes = sorted(set(influence.uncertainty_notes))
        influence.discourse_annotations = sorted(set(influence.discourse_annotations))
        signal_by_key = {
            (signal.signal_type, signal.item_type, signal.item_id): signal
            for signal in influence.signals
        }
        influence.signals = [signal_by_key[key] for key in sorted(signal_by_key)]
        warning_by_key = {
            (warning.warning_type.value, warning.message, tuple(sorted(warning.related_ids))): warning
            for warning in influence.warnings
        }
        influence.warnings = [warning_by_key[key] for key in sorted(warning_by_key)]


@dataclass(slots=True)
class DreamReviewAdapter:
    """Expose dream replay output as attention candidates for review ordering."""

    def to_attention_candidates(self, result: DreamReplayResult) -> list[AttentionCandidate]:
        candidate_by_id: dict[str, AttentionCandidate] = {}
        for memory_id in sorted(result.replayed_memory_ids):
            candidate_by_id[memory_id] = AttentionCandidate(
                record_id=memory_id,
                record_type="memory",
                label=f"dream replay memory {memory_id}",
                text="internal dream replay review candidate",
                provenance_ids=set(),
                contradiction_pressure=1.0 if memory_id in result.contradiction_memory_ids else 0.0,
                recurrence=0.25,
                novelty=0.4,
                uncertainty_load=0.6 if memory_id in result.stale_memory_ids else 0.3,
                archived=memory_id in result.archival_memory_ids,
                contested=memory_id in result.contradiction_memory_ids,
                metadata={
                    "dream_artifact_id": result.artifact.artifact_id,
                    "dream_review_context_only": True,
                    "relevance": self._recommendation_priority(result, memory_id),
                },
            )
        return [candidate_by_id[key] for key in sorted(candidate_by_id)]

    def _recommendation_priority(self, result: DreamReplayResult, memory_id: str) -> float:
        priorities = [
            recommendation.priority
            for recommendation in result.recommendations
            if memory_id in recommendation.memory_ids
        ]
        return _clamp(max(priorities) if priorities else 0.0)

