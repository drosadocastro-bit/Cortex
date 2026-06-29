"""Deterministic predictive memory for review attention."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    AttentionCandidate,
    ExpectationTrace,
    MemoryRecord,
    PredictionCandidate,
    PredictionError,
    PredictiveMemoryResult,
    PredictiveSignalType,
    PredictiveWarningType,
    SurpriseSignal,
)


@dataclass(slots=True)
class ExpectationGuardrails:
    """Guardrails that keep predictive memory from becoming belief."""

    def warnings_for(self, result: PredictiveMemoryResult) -> list[PredictiveWarningType]:
        warnings = {
            PredictiveWarningType.EXPECTATION_NOT_TRUTH,
            PredictiveWarningType.PREDICTION_NOT_EVIDENCE,
            PredictiveWarningType.SURPRISE_NOT_DISPROOF,
            PredictiveWarningType.REVIEW_ATTENTION_ONLY,
        }
        if any(candidate.signal_type is PredictiveSignalType.EXPECTED_LINEAGE_ECHO for candidate in result.prediction_candidates):
            warnings.add(PredictiveWarningType.RECURRENCE_NOT_CORROBORATION)
        if result.prediction_candidates:
            warnings.add(PredictiveWarningType.EXPECTED_NOT_CONFIRMED)
        return sorted(warnings, key=lambda warning: warning.value)

    def blocks_evidence_promotion(self, result: PredictiveMemoryResult) -> bool:
        """Predictive output cannot become evidence automatically."""
        return bool(result.expectation_traces or result.prediction_candidates or result.surprise_signals)


@dataclass(slots=True)
class PredictiveReviewAdapter:
    """Expose prediction candidates as attention candidates for review ordering."""

    def to_attention_candidates(self, result: PredictiveMemoryResult) -> list[AttentionCandidate]:
        candidates: list[AttentionCandidate] = []
        for prediction in sorted(result.prediction_candidates, key=lambda item: (item.target_id, item.signal_type.value)):
            candidates.append(
                AttentionCandidate(
                    record_id=prediction.target_id,
                    record_type=prediction.target_type,
                    label=f"predictive review candidate {prediction.target_id}",
                    text="internal predictive memory review candidate",
                    provenance_ids=set(),
                    contradiction_pressure=1.0 if prediction.signal_type is PredictiveSignalType.EXPECTED_CONTRADICTION else 0.0,
                    recurrence=0.6 if prediction.signal_type is PredictiveSignalType.EXPECTED_LINEAGE_ECHO else 0.2,
                    novelty=0.5,
                    uncertainty_load=prediction.review_priority,
                    contested=prediction.signal_type is PredictiveSignalType.EXPECTED_CONTRADICTION,
                    metadata={
                        "predictive_memory_context_only": True,
                        "predictive_signal": prediction.signal_type.value,
                        "relevance": prediction.review_priority,
                    },
                )
            )
        return candidates


@dataclass(slots=True)
class PredictiveMemoryEngine:
    """Build deterministic expectations from existing memory structure.

    Predictive memory anticipates review needs, not future truth. It does not
    mutate memory records, create evidence, confirm claims, or resolve
    contradictions.
    """

    stale_after_days: int = 30
    guardrails: ExpectationGuardrails = field(default_factory=ExpectationGuardrails)

    def analyze(
        self,
        memories: list[MemoryRecord],
        *,
        incoming_memories: list[MemoryRecord] | None = None,
        as_of: datetime | None = None,
    ) -> PredictiveMemoryResult:
        timestamp = as_of or datetime.now(timezone.utc)
        incoming_memories = incoming_memories or []
        input_fingerprint = self._fingerprint(memories + incoming_memories)

        sorted_memories = sorted(memories, key=lambda memory: (memory.normalized_key or memory.content_key(memory.content), memory.id))
        traces: list[ExpectationTrace] = []
        candidates: list[PredictionCandidate] = []

        for memory in sorted_memories:
            memory_traces, memory_candidates = self._expectations_for_memory(memory, as_of=timestamp)
            traces.extend(memory_traces)
            candidates.extend(memory_candidates)

        duplicate_groups = self._duplicate_groups(sorted_memories)
        for key, group in duplicate_groups.items():
            trace = self._trace(
                PredictiveSignalType.EXPECTED_LINEAGE_ECHO,
                set(group),
                "recurrent memory key may deserve duplicate or lineage review",
                0.62,
                [f"normalized_key:{key}"],
                [PredictiveWarningType.RECURRENCE_NOT_CORROBORATION],
            )
            traces.append(trace)
            for memory_id in group:
                candidates.append(
                    self._candidate(
                        memory_id,
                        PredictiveSignalType.EXPECTED_LINEAGE_ECHO,
                        0.62,
                        set(group),
                        ["recurrent memory key predicts duplicate or lineage review need"],
                        [PredictiveWarningType.RECURRENCE_NOT_CORROBORATION],
                    )
                )

        errors, surprises = self._prediction_errors(traces, incoming_memories)
        result = PredictiveMemoryResult(
            expectation_traces=self._dedupe_traces(traces),
            prediction_candidates=self._dedupe_candidates(candidates),
            prediction_errors=errors,
            surprise_signals=surprises,
            limitations=[
                "Predictive memory anticipates review needs, not truth.",
                "Expected patterns do not confirm claims or evidence.",
                "Surprise raises attention but does not disprove records.",
            ],
            mutated_state=input_fingerprint != self._fingerprint(memories + incoming_memories),
        )
        result.warnings = self.guardrails.warnings_for(result)
        return result

    def _expectations_for_memory(
        self,
        memory: MemoryRecord,
        *,
        as_of: datetime,
    ) -> tuple[list[ExpectationTrace], list[PredictionCandidate]]:
        traces: list[ExpectationTrace] = []
        candidates: list[PredictionCandidate] = []
        if not memory.evidence_ids:
            traces.append(
                self._trace(
                    PredictiveSignalType.EXPECTED_MISSING_PROVENANCE,
                    {memory.id},
                    "missing evidence reference predicts provenance review need",
                    0.7,
                    ["memory has no evidence ids"],
                    [PredictiveWarningType.PREDICTION_NOT_EVIDENCE],
                )
            )
            candidates.append(
                self._candidate(
                    memory.id,
                    PredictiveSignalType.EXPECTED_MISSING_PROVENANCE,
                    0.7,
                    {memory.id},
                    ["provenance gap should remain visible"],
                    [PredictiveWarningType.PREDICTION_NOT_EVIDENCE],
                )
            )
        if memory.contradiction_pressure > 0 or memory.needs_review:
            priority = max(0.6, _clamp(memory.contradiction_pressure))
            traces.append(
                self._trace(
                    PredictiveSignalType.EXPECTED_CONTRADICTION,
                    {memory.id, *memory.linked_memory_ids},
                    "contradiction pressure predicts unresolved review need",
                    priority,
                    ["contradiction pressure remains visible"],
                    [PredictiveWarningType.EXPECTATION_NOT_TRUTH],
                )
            )
            candidates.append(
                self._candidate(
                    memory.id,
                    PredictiveSignalType.EXPECTED_CONTRADICTION,
                    priority,
                    {memory.id, *memory.linked_memory_ids},
                    ["contradiction pressure predicts review attention"],
                    [PredictiveWarningType.SURPRISE_NOT_DISPROOF],
                )
            )
        if self._is_stale(memory, as_of=as_of):
            traces.append(
                self._trace(
                    PredictiveSignalType.EXPECTED_STALE_MEMORY,
                    {memory.id},
                    "stale memory predicts refresh or archival review need",
                    0.45,
                    ["memory inactive past stale window"],
                    [PredictiveWarningType.REVIEW_ATTENTION_ONLY],
                )
            )
            candidates.append(
                self._candidate(
                    memory.id,
                    PredictiveSignalType.EXPECTED_STALE_MEMORY,
                    0.45,
                    {memory.id},
                    ["stale memory should be reviewed before being forgotten"],
                    [PredictiveWarningType.REVIEW_ATTENTION_ONLY],
                )
            )
        return traces, candidates

    def _prediction_errors(
        self,
        traces: list[ExpectationTrace],
        incoming_memories: list[MemoryRecord],
    ) -> tuple[list[PredictionError], list[SurpriseSignal]]:
        expected_signals = {trace.signal_type for trace in traces}
        trace_ids_by_signal: dict[PredictiveSignalType, set[str]] = defaultdict(set)
        for trace in traces:
            trace_ids_by_signal[trace.signal_type].add(trace.trace_id)

        errors: list[PredictionError] = []
        surprises: list[SurpriseSignal] = []
        for incoming in sorted(incoming_memories, key=lambda memory: memory.id):
            if not incoming.evidence_ids and PredictiveSignalType.EXPECTED_MISSING_PROVENANCE not in expected_signals:
                errors.append(
                    PredictionError(
                        PredictiveSignalType.EXPECTED_MISSING_PROVENANCE,
                        incoming.id,
                        "incoming memory has a provenance gap that was not expected",
                        severity=0.65,
                        warning_flags=[PredictiveWarningType.PREDICTION_NOT_EVIDENCE],
                    )
                )
                surprises.append(self._surprise(incoming.id, 0.65, "unexpected provenance gap"))
            if (incoming.contradiction_pressure > 0 or incoming.needs_review) and PredictiveSignalType.EXPECTED_CONTRADICTION not in expected_signals:
                errors.append(
                    PredictionError(
                        PredictiveSignalType.EXPECTED_CONTRADICTION,
                        incoming.id,
                        "incoming contradiction pressure was not predicted by prior memory",
                        severity=max(0.6, _clamp(incoming.contradiction_pressure)),
                        warning_flags=[PredictiveWarningType.SURPRISE_NOT_DISPROOF],
                    )
                )
                surprises.append(self._surprise(incoming.id, max(0.6, _clamp(incoming.contradiction_pressure)), "unexpected contradiction pressure"))
            if incoming.normalized_key and any(incoming.id in trace.source_memory_ids for trace in traces):
                continue
        for error in errors:
            error.related_trace_ids.update(trace_ids_by_signal.get(error.expected_signal, set()))
        return errors, surprises

    def _trace(
        self,
        signal_type: PredictiveSignalType,
        source_memory_ids: set[str],
        expected_review_need: str,
        strength: float,
        rationale: list[str],
        warnings: list[PredictiveWarningType],
    ) -> ExpectationTrace:
        trace_id = str(uuid5(NAMESPACE_URL, f"expectation:{signal_type.value}:{':'.join(sorted(source_memory_ids))}:{expected_review_need}"))
        return ExpectationTrace(
            trace_id=trace_id,
            source_memory_ids=source_memory_ids,
            signal_type=signal_type,
            expected_review_need=expected_review_need,
            expectation_strength=strength,
            rationale=rationale,
            warning_flags=warnings,
        )

    def _candidate(
        self,
        target_id: str,
        signal_type: PredictiveSignalType,
        priority: float,
        supporting_memory_ids: set[str],
        rationale: list[str],
        warnings: list[PredictiveWarningType],
    ) -> PredictionCandidate:
        candidate_id = str(uuid5(NAMESPACE_URL, f"prediction:{target_id}:{signal_type.value}:{':'.join(sorted(supporting_memory_ids))}"))
        return PredictionCandidate(
            candidate_id=candidate_id,
            target_id=target_id,
            signal_type=signal_type,
            review_priority=priority,
            supporting_memory_ids=supporting_memory_ids,
            rationale=rationale,
            warning_flags=warnings,
        )

    def _surprise(self, target_id: str, score: float, reason: str) -> SurpriseSignal:
        signal_id = str(uuid5(NAMESPACE_URL, f"surprise:{target_id}:{reason}:{score:.3f}"))
        return SurpriseSignal(
            signal_id=signal_id,
            target_id=target_id,
            surprise_score=score,
            reason=reason,
            warning_flags=[PredictiveWarningType.SURPRISE_NOT_DISPROOF],
        )

    def _duplicate_groups(self, memories: list[MemoryRecord]) -> dict[str, list[str]]:
        by_key: dict[str, list[str]] = defaultdict(list)
        for memory in memories:
            by_key[memory.normalized_key or MemoryRecord.content_key(memory.content)].append(memory.id)
        return {key: sorted(ids) for key, ids in sorted(by_key.items()) if len(ids) > 1}

    def _is_stale(self, memory: MemoryRecord, *, as_of: datetime) -> bool:
        anchor = memory.last_activated_at or memory.last_accessed_at or memory.created_at
        return (as_of - anchor).total_seconds() / 86400 >= self.stale_after_days

    def _dedupe_traces(self, traces: list[ExpectationTrace]) -> list[ExpectationTrace]:
        by_id = {trace.trace_id: trace for trace in traces}
        return [by_id[key] for key in sorted(by_id)]

    def _dedupe_candidates(self, candidates: list[PredictionCandidate]) -> list[PredictionCandidate]:
        by_id = {candidate.candidate_id: candidate for candidate in candidates}
        return [by_id[key] for key in sorted(by_id)]

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
                    memory.contradiction_pressure,
                    memory.needs_review,
                    tuple(sorted(memory.evidence_ids)),
                    tuple(memory.linked_memory_ids),
                )
                for memory in memories
            )
        )

