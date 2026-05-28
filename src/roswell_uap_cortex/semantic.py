"""Controlled semantic similarity layer."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from roswell_uap_cortex.embedding_backend import EmbeddingBackend, MockEmbeddingBackend
from roswell_uap_cortex.independence import EvidenceIndependenceInput, IndependenceScorer
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import SemanticRecord, SemanticSimilarityResult
from roswell_uap_cortex.semantic_guardrails import SemanticContaminationGuard
from roswell_uap_cortex.text import SimpleTokenizer, overlap_score


@dataclass(slots=True)
class SemanticSimilarityEngine:
    """Compare semantic records without creating confirmation or graph edges."""

    embedding_backend: EmbeddingBackend = field(default_factory=MockEmbeddingBackend)
    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)
    independence_scorer: IndependenceScorer = field(default_factory=IndependenceScorer)
    guard: SemanticContaminationGuard = field(default_factory=SemanticContaminationGuard)

    def compare(self, first: SemanticRecord, second: SemanticRecord) -> SemanticSimilarityResult:
        vector_score = self._cosine(
            self.embedding_backend.embed_text(first.text).values,
            self.embedding_backend.embed_text(second.text).values,
        )
        lexical = overlap_score(
            self.tokenizer.tokenize(first.text),
            self.tokenizer.tokenize(second.text),
        )
        tag_overlap = overlap_score(first.tags, second.tags)
        entity_overlap = overlap_score(first.entity_ids, second.entity_ids)
        source_independence = self.independence_scorer.score_pair(
            EvidenceIndependenceInput(
                source_id=first.source_id or first.record_id,
                lineage_id=first.lineage_id,
            ),
            EvidenceIndependenceInput(
                source_id=second.source_id or second.record_id,
                lineage_id=second.lineage_id,
            ),
        )
        lineage_overlap = bool(first.lineage_id and first.lineage_id == second.lineage_id)
        contradiction_pressure = max(
            _clamp(first.contradiction_pressure),
            _clamp(second.contradiction_pressure),
        )
        score = (
            vector_score * 0.42
            + lexical * 0.22
            + tag_overlap * 0.12
            + entity_overlap * 0.12
            + source_independence * 0.12
        )
        score *= 1 - contradiction_pressure * 0.5
        result = SemanticSimilarityResult(
            record_a_id=first.record_id,
            record_b_id=second.record_id,
            similarity_score=_clamp(score),
            similarity_reason=self._reasons(vector_score, lexical, tag_overlap, entity_overlap),
            source_independence=source_independence,
            lineage_overlap=lineage_overlap,
            contradiction_pressure=contradiction_pressure,
        )
        return self.guard.apply(result, first, second)

    def _cosine(self, first: list[float], second: list[float]) -> float:
        if not first or not second:
            return 0.0
        numerator = sum(a * b for a, b in zip(first, second))
        first_norm = math.sqrt(sum(a * a for a in first))
        second_norm = math.sqrt(sum(b * b for b in second))
        if not first_norm or not second_norm:
            return 0.0
        return _clamp(numerator / (first_norm * second_norm))

    def _reasons(
        self,
        vector_score: float,
        lexical: float,
        tag_overlap: float,
        entity_overlap: float,
    ) -> list[str]:
        reasons = ["semantic_similarity_not_confirmation"]
        if vector_score > 0:
            reasons.append("mock_embedding_similarity")
        if lexical > 0:
            reasons.append("lexical_overlap")
        if tag_overlap > 0:
            reasons.append("shared_tags")
        if entity_overlap > 0:
            reasons.append("shared_entities")
        return reasons
