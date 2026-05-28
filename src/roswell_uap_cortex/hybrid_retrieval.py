"""Hybrid retrieval coordinator preserving component scores."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    AssociationCandidate,
    HybridRetrievalResult,
    SemanticSimilarityResult,
)


@dataclass(slots=True)
class HybridRetrievalCoordinator:
    """Combine retrieval signals without producing truth confidence."""

    def combine(
        self,
        *,
        associative_candidates: list[AssociationCandidate] | None = None,
        graph_node_ids: set[str] | None = None,
        timeline_scores: dict[str, float] | None = None,
        semantic_results: list[SemanticSimilarityResult] | None = None,
        provenance_visible_ids: set[str] | None = None,
    ) -> list[HybridRetrievalResult]:
        associative_candidates = associative_candidates or []
        graph_node_ids = graph_node_ids or set()
        timeline_scores = timeline_scores or {}
        semantic_results = semantic_results or []
        provenance_visible_ids = provenance_visible_ids or set()
        by_id: dict[str, HybridRetrievalResult] = {}

        for candidate in associative_candidates:
            result = by_id.setdefault(candidate.record_id, HybridRetrievalResult(record_id=candidate.record_id))
            result.associative_score = max(
                result.associative_score,
                candidate.score.final_association_score,
            )
            result.uncertainty_notes.extend(
                note for note in candidate.uncertainty_notes if note not in result.uncertainty_notes
            )
        for node_id in graph_node_ids:
            result = by_id.setdefault(node_id, HybridRetrievalResult(record_id=node_id))
            result.graph_score = 1.0
        for record_id, score in timeline_scores.items():
            result = by_id.setdefault(record_id, HybridRetrievalResult(record_id=record_id))
            result.timeline_score = _clamp(score)
        for semantic in semantic_results:
            for record_id in [semantic.record_a_id, semantic.record_b_id]:
                result = by_id.setdefault(record_id, HybridRetrievalResult(record_id=record_id))
                result.semantic_similarity_score = max(
                    result.semantic_similarity_score,
                    semantic.similarity_score,
                )
                for warning in semantic.warning_flags:
                    if warning not in result.semantic_warnings:
                        result.semantic_warnings.append(warning)
                if semantic.warning_flags and "semantic warnings present" not in result.uncertainty_notes:
                    result.uncertainty_notes.append("semantic warnings present")
        for record_id in provenance_visible_ids:
            result = by_id.setdefault(record_id, HybridRetrievalResult(record_id=record_id))
            result.provenance_visible = True

        for result in by_id.values():
            provenance_bonus = 0.08 if result.provenance_visible else 0.0
            result.ranking_score = _clamp(
                result.associative_score * 0.28
                + result.graph_score * 0.2
                + result.timeline_score * 0.16
                + result.semantic_similarity_score * 0.28
                + provenance_bonus
            )
            if not result.provenance_visible:
                result.uncertainty_notes.append("missing provenance visibility")

        return sorted(
            by_id.values(),
            key=lambda result: (result.ranking_score, result.record_id),
            reverse=True,
        )
