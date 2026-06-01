"""Build compact reasoning contexts from activated associations."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ActivatedContext,
    AssociationCandidate,
    AttentionDecision,
    ClaimNode,
    EvidenceItem,
    MemoryRecord,
    ProvenanceRecord,
    ReasoningContext,
    ReviewInfluenceResult,
    SourceLineageRecord,
    UncertaintyNote,
)


@dataclass(slots=True)
class ContextWindowBuilder:
    """Select focused context while limiting duplicate lineage flooding."""

    max_items: int = 8
    max_per_lineage: int = 1

    def build(
        self,
        activated_context: ActivatedContext,
        *,
        candidates: list[AssociationCandidate] | None = None,
        evidence_by_id: dict[str, EvidenceItem] | None = None,
        claims_by_id: dict[str, ClaimNode] | None = None,
        memories_by_id: dict[str, MemoryRecord] | None = None,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
        lineage_by_evidence_id: dict[str, SourceLineageRecord] | None = None,
        attention_decision: AttentionDecision | None = None,
        review_influence: ReviewInfluenceResult | None = None,
        max_items: int | None = None,
    ) -> ReasoningContext:
        evidence_by_id = evidence_by_id or {}
        claims_by_id = claims_by_id or {}
        memories_by_id = memories_by_id or {}
        provenance_by_evidence_id = provenance_by_evidence_id or {}
        lineage_by_evidence_id = lineage_by_evidence_id or {}
        limit = max_items or self.max_items

        selected_candidates = self._select_candidates(
            activated_context,
            candidates or [],
            lineage_by_evidence_id,
            limit,
            attention_decision,
        )
        evidence_ids = set(activated_context.activated_evidence_ids)
        claim_ids = set(activated_context.activated_claim_ids)
        memory_ids = set(activated_context.activated_memory_ids)
        if review_influence is not None:
            influenced_ids = (
                review_influence.prioritized_ids
                | review_influence.must_include_ids
                | review_influence.unresolved_ids
            )
            evidence_ids.update(influenced_ids & set(evidence_by_id))
            claim_ids.update(influenced_ids & set(claims_by_id))
            memory_ids.update(influenced_ids & set(memories_by_id))

        for candidate in selected_candidates:
            evidence_ids.update(candidate.evidence_ids)
            claim_ids.update(candidate.claim_ids)
            memory_ids.update(candidate.memory_ids)

        selected_evidence = self._trim_evidence_by_lineage(
            [evidence_by_id[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence_by_id],
            lineage_by_evidence_id,
            limit,
        )
        selected_evidence_ids = {item.id for item in selected_evidence}
        selected_lineage = [
            lineage_by_evidence_id[evidence_id]
            for evidence_id in selected_evidence_ids
            if evidence_id in lineage_by_evidence_id
        ]
        selected_provenance = [
            provenance_by_evidence_id[evidence_id]
            for evidence_id in selected_evidence_ids
            if evidence_id in provenance_by_evidence_id
        ]

        notes = [
            UncertaintyNote(note=note, severity="caution")
            for note in activated_context.uncertainty_notes
        ]
        if review_influence is not None:
            for note in review_influence.uncertainty_notes:
                notes.append(UncertaintyNote(note=note, related_ids=set(review_influence.unresolved_ids)))
            for annotation in review_influence.discourse_annotations:
                notes.append(UncertaintyNote(note=annotation, severity="review"))
            for warning in review_influence.warnings:
                notes.append(
                    UncertaintyNote(
                        note=warning.message,
                        related_ids=set(warning.related_ids),
                        severity="review_boundary",
                    )
                )
        if len(selected_evidence) < len(evidence_ids):
            notes.append(
                UncertaintyNote(
                    note="low-value duplicate lineage context was trimmed",
                    related_ids=evidence_ids - selected_evidence_ids,
                )
            )

        return ReasoningContext(
            activated_context=activated_context,
            selected_candidates=selected_candidates,
            evidence_items=selected_evidence,
            claims=[claims_by_id[claim_id] for claim_id in claim_ids if claim_id in claims_by_id],
            memories=[memories_by_id[memory_id] for memory_id in memory_ids if memory_id in memories_by_id],
            provenance_records=selected_provenance,
            lineage_records=selected_lineage,
            uncertainty_notes=notes,
        )

    def _select_candidates(
        self,
        activated_context: ActivatedContext,
        candidates: list[AssociationCandidate],
        lineage_by_evidence_id: dict[str, SourceLineageRecord],
        limit: int,
        attention_decision: AttentionDecision | None = None,
    ) -> list[AssociationCandidate]:
        all_candidates = list(candidates)
        all_candidates.extend(activated_context.contested_associations)
        all_candidates.extend(activated_context.weak_associations)
        merged: dict[tuple[str, str], AssociationCandidate] = {}
        for candidate in all_candidates:
            key = (candidate.record_type, candidate.record_id)
            existing = merged.get(key)
            if existing is None or (
                candidate.score.final_association_score
                > existing.score.final_association_score
            ):
                merged[key] = candidate

        ranked = sorted(
            merged.values(),
            key=lambda item: (
                self._attention_rank(item, attention_decision),
                bool(item.claim_status and item.claim_status.value == "contested"),
                item.score.final_association_score,
                len(item.evidence_ids),
            ),
            reverse=True,
        )

        selected: list[AssociationCandidate] = []
        lineage_counts: dict[str, int] = {}
        for candidate in ranked:
            candidate_lineages = {
                lineage_by_evidence_id[evidence_id].lineage_id
                for evidence_id in candidate.evidence_ids
                if evidence_id in lineage_by_evidence_id
            }
            if candidate_lineages and all(
                lineage_counts.get(lineage_id, 0) >= self.max_per_lineage
                for lineage_id in candidate_lineages
            ):
                continue
            selected.append(candidate)
            for lineage_id in candidate_lineages:
                lineage_counts[lineage_id] = lineage_counts.get(lineage_id, 0) + 1
            if len(selected) >= limit:
                break
        return selected

    def _attention_rank(
        self,
        candidate: AssociationCandidate,
        attention_decision: AttentionDecision | None,
    ) -> float:
        if attention_decision is None:
            return 0.0
        score = attention_decision.salience_by_id.get(candidate.record_id)
        return 0.0 if score is None else score.final_salience_score

    def _trim_evidence_by_lineage(
        self,
        evidence: list[EvidenceItem],
        lineage_by_evidence_id: dict[str, SourceLineageRecord],
        limit: int,
    ) -> list[EvidenceItem]:
        selected: list[EvidenceItem] = []
        lineage_counts: dict[str, int] = {}
        for item in sorted(evidence, key=lambda evidence_item: evidence_item.id):
            lineage = lineage_by_evidence_id.get(item.id)
            lineage_id = lineage.lineage_id if lineage else f"unknown:{item.id}"
            if lineage_counts.get(lineage_id, 0) >= self.max_per_lineage:
                continue
            selected.append(item)
            lineage_counts[lineage_id] = lineage_counts.get(lineage_id, 0) + 1
            if len(selected) >= limit:
                break
        return selected
