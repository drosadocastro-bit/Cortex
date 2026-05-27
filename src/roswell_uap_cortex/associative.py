"""Deterministic associative retrieval without vector dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from roswell_uap_cortex.correlation_guard import CorrelationGuard
from roswell_uap_cortex.independence import EvidenceIndependenceInput, IndependenceScorer
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    ActivatedContext,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    Claim,
    ClaimMatrixStatus,
    ClaimNode,
    EntityNode,
    EvidenceItem,
    MemoryRecord,
    RetrievalContext,
)
from roswell_uap_cortex.text import SimpleTokenizer, overlap_score


@dataclass(slots=True)
class AssociativeRetrievalEngine:
    """Rank possible associations without creating support relationships."""

    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)
    independence_scorer: IndependenceScorer = field(default_factory=IndependenceScorer)
    guard: CorrelationGuard = field(default_factory=CorrelationGuard)

    def retrieve(
        self,
        query: str,
        *,
        memories: list[MemoryRecord] | None = None,
        evidence: list[EvidenceItem] | None = None,
        claims: list[ClaimNode | Claim] | None = None,
        entities: list[EntityNode] | None = None,
        context: RetrievalContext | None = None,
        limit: int | None = None,
    ) -> list[AssociationCandidate]:
        retrieval_context = context or RetrievalContext(query=query)
        query_tokens = self.tokenizer.tokenize(query)
        candidates: dict[tuple[str, str], AssociationCandidate] = {}

        for memory in memories or []:
            self._merge_candidate(
                candidates,
                self._score_record(
                    memory,
                    "memory",
                    memory.id,
                    memory.content,
                    query_tokens,
                    retrieval_context,
                ),
            )
        for item in evidence or []:
            self._merge_candidate(
                candidates,
                self._score_record(
                    item,
                    "evidence",
                    item.id,
                    item.summary,
                    query_tokens,
                    retrieval_context,
                ),
            )
        for claim in claims or []:
            label = claim.text
            self._merge_candidate(
                candidates,
                self._score_record(
                    claim,
                    "claim",
                    claim.id,
                    label,
                    query_tokens,
                    retrieval_context,
                ),
            )
        for entity in entities or []:
            label = " ".join([entity.label, *sorted(entity.aliases)])
            self._merge_candidate(
                candidates,
                self._score_record(
                    entity,
                    "entity",
                    entity.id,
                    label,
                    query_tokens,
                    retrieval_context,
                ),
            )

        ranked = sorted(
            candidates.values(),
            key=lambda candidate: (
                candidate.score.final_association_score,
                candidate.score.lexical_overlap,
                candidate.label.casefold(),
            ),
            reverse=True,
        )
        if limit is not None:
            return ranked[:limit]
        return ranked

    def _score_record(
        self,
        record: Any,
        record_type: str,
        record_id: str,
        label: str,
        query_tokens: set[str],
        context: RetrievalContext,
    ) -> AssociationCandidate:
        metadata = getattr(record, "metadata", {}) or {}
        record_tokens = self.tokenizer.tokenize(label)
        record_tags = set(getattr(record, "tags", []) or metadata.get("tags", set()))
        record_entities = set(metadata.get("entity_ids", set()))
        canonical_topic = getattr(record, "canonical_topic", metadata.get("canonical_topic", None))
        if canonical_topic:
            record_tokens.update(self.tokenizer.tokenize(canonical_topic))

        lexical = overlap_score(query_tokens, record_tokens)
        if canonical_topic and canonical_topic in context.query_canonical_topics:
            lexical = max(lexical, 0.6)
        tag_overlap = overlap_score(context.query_tags, record_tags)
        entity_overlap = overlap_score(context.query_entity_ids, record_entities)
        timeline = self._timeline_proximity(context.query_date, self._record_date(record, metadata))
        source_id = getattr(record, "source_id", metadata.get("source_id", None))
        lineage_id = metadata.get("lineage_id", None)
        source_kind = metadata.get("source_kind", "unknown")
        source_independence = self.independence_scorer.score_pair(
            EvidenceIndependenceInput(
                source_id=context.source_id or "query",
                lineage_id=context.lineage_id,
                source_kind="unknown",
            ),
            EvidenceIndependenceInput(
                source_id=source_id or record_id,
                lineage_id=lineage_id,
                source_kind=source_kind,
            ),
        )
        contradiction_pressure = float(
            getattr(record, "contradiction_pressure", metadata.get("contradiction_pressure", 0.0))
            or 0.0
        )

        base = (
            lexical * 0.36
            + tag_overlap * 0.18
            + entity_overlap * 0.18
            + timeline * 0.1
            + source_independence * 0.12
            + (1 - _clamp(contradiction_pressure)) * 0.06
        )
        score = AssociationScore(
            lexical_overlap=_clamp(lexical),
            tag_overlap=_clamp(tag_overlap),
            entity_overlap=_clamp(entity_overlap),
            timeline_proximity=_clamp(timeline),
            source_independence=_clamp(source_independence),
            contradiction_penalty=_clamp(contradiction_pressure),
            final_association_score=_clamp(base),
        )
        score, guard_notes = self.guard.apply(
            score,
            lineage_id=lineage_id,
            contradiction_pressure=contradiction_pressure,
        )

        reasons = self._reasons(score, canonical_topic, context)
        candidate = AssociationCandidate(
            record_id=record_id,
            record_type=record_type,
            label=label,
            score=score,
            association_label=AssociationLabel.POSSIBLE_ASSOCIATION,
            association_reason=reasons,
            source_id=source_id,
            lineage_id=lineage_id,
            claim_status=getattr(record, "status", None),
            uncertainty_notes=guard_notes,
        )
        self._attach_ids(candidate, record, record_type, record_entities)
        return candidate

    def _attach_ids(
        self,
        candidate: AssociationCandidate,
        record: Any,
        record_type: str,
        record_entities: set[str],
    ) -> None:
        if record_type == "memory":
            candidate.memory_ids.add(record.id)
            candidate.evidence_ids.update(getattr(record, "evidence_ids", set()))
        elif record_type == "claim":
            candidate.claim_ids.add(record.id)
            candidate.evidence_ids.update(getattr(record, "evidence_ids", set()))
        elif record_type == "evidence":
            candidate.evidence_ids.add(record.id)
        elif record_type == "entity":
            candidate.entity_ids.add(record.id)
        candidate.entity_ids.update(record_entities)

    def _merge_candidate(
        self,
        candidates: dict[tuple[str, str], AssociationCandidate],
        candidate: AssociationCandidate,
    ) -> None:
        key = (candidate.record_type, candidate.record_id)
        existing = candidates.get(key)
        if existing is None:
            candidates[key] = candidate
            return

        if candidate.score.final_association_score > existing.score.final_association_score:
            existing.score = candidate.score
        existing.memory_ids.update(candidate.memory_ids)
        existing.claim_ids.update(candidate.claim_ids)
        existing.evidence_ids.update(candidate.evidence_ids)
        existing.entity_ids.update(candidate.entity_ids)
        for reason in candidate.association_reason:
            if reason not in existing.association_reason:
                existing.association_reason.append(reason)
        for note in candidate.uncertainty_notes:
            if note not in existing.uncertainty_notes:
                existing.uncertainty_notes.append(note)

    def _reasons(
        self,
        score: AssociationScore,
        canonical_topic: str | None,
        context: RetrievalContext,
    ) -> list[str]:
        reasons = ["possible_association"]
        if score.lexical_overlap > 0:
            reasons.append("lexical_overlap")
        if score.tag_overlap > 0:
            reasons.append("shared_tags")
        if score.entity_overlap > 0:
            reasons.append("shared_entities")
        if score.timeline_proximity > 0:
            reasons.append("timeline_proximity")
        if canonical_topic and canonical_topic in context.query_canonical_topics:
            reasons.append("related_canonical_topic")
        if score.contradiction_penalty > 0:
            reasons.append("contradiction_pressure")
        return reasons

    def _record_date(self, record: Any, metadata: dict[str, Any]) -> date | None:
        value = metadata.get("event_date") or metadata.get("observed_date")
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        observed_at = getattr(record, "observed_at", None)
        if isinstance(observed_at, datetime):
            return observed_at.date()
        if isinstance(observed_at, date):
            return observed_at
        return None

    def _timeline_proximity(self, query_date: date | None, record_date: date | None) -> float:
        if query_date is None or record_date is None:
            return 0.0
        days = abs((query_date - record_date).days)
        return _clamp(1 / (1 + days / 30))


@dataclass(slots=True)
class ActivationContextBuilder:
    """Convert ranked possible associations into a focused activated context."""

    weak_threshold: float = 0.35
    activation_threshold: float = 0.5

    def build(
        self,
        candidates: list[AssociationCandidate],
        *,
        limit: int | None = None,
    ) -> ActivatedContext:
        activated = ActivatedContext()
        merged: dict[tuple[str, str], AssociationCandidate] = {}

        for candidate in candidates:
            key = (candidate.record_type, candidate.record_id)
            existing = merged.get(key)
            if existing is None:
                merged[key] = candidate
            else:
                self._merge(existing, candidate)

        ranked = sorted(
            merged.values(),
            key=lambda item: item.score.final_association_score,
            reverse=True,
        )
        if limit is not None:
            ranked = ranked[:limit]

        for candidate in ranked:
            is_contested = candidate.claim_status is ClaimMatrixStatus.CONTESTED
            if is_contested:
                candidate.association_label = AssociationLabel.CONTESTED_ASSOCIATION
                activated.contested_associations.append(candidate)
                activated.activated_claim_ids.update(candidate.claim_ids)
                activated.activated_evidence_ids.update(candidate.evidence_ids)
                activated.activated_entity_ids.update(candidate.entity_ids)
                self._copy_notes(activated, candidate)
                continue

            if candidate.score.final_association_score < self.activation_threshold:
                candidate.association_label = AssociationLabel.WEAK_ASSOCIATION
                activated.weak_associations.append(candidate)
                self._copy_notes(activated, candidate)
                continue

            activated.activated_memory_ids.update(candidate.memory_ids)
            activated.activated_claim_ids.update(candidate.claim_ids)
            activated.activated_evidence_ids.update(candidate.evidence_ids)
            activated.activated_entity_ids.update(candidate.entity_ids)
            self._copy_notes(activated, candidate)

        return activated

    def _merge(self, existing: AssociationCandidate, incoming: AssociationCandidate) -> None:
        if incoming.score.final_association_score > existing.score.final_association_score:
            existing.score = incoming.score
        existing.memory_ids.update(incoming.memory_ids)
        existing.claim_ids.update(incoming.claim_ids)
        existing.evidence_ids.update(incoming.evidence_ids)
        existing.entity_ids.update(incoming.entity_ids)
        for reason in incoming.association_reason:
            if reason not in existing.association_reason:
                existing.association_reason.append(reason)
        for note in incoming.uncertainty_notes:
            if note not in existing.uncertainty_notes:
                existing.uncertainty_notes.append(note)

    def _copy_notes(self, activated: ActivatedContext, candidate: AssociationCandidate) -> None:
        for note in candidate.uncertainty_notes:
            if note not in activated.uncertainty_notes:
                activated.uncertainty_notes.append(note)
