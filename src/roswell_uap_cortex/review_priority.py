"""Deterministic claim review priority scoring."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    ClaimEvaluationWarningType,
    ClaimReviewItem,
    EvidenceAssessmentSummary,
    ReviewPriority,
)


@dataclass(slots=True)
class ReviewPriorityEngine:
    """Score review priority without turning salience into truth confidence."""

    def score(self, item: ClaimReviewItem) -> tuple[ReviewPriority, float, list[str]]:
        reasons: list[str] = []
        score = 0.0

        if item.contradiction_summaries:
            score += 0.3
            reasons.append("contradiction_visible")

        if item.support_summaries and item.contradiction_summaries:
            score += 0.25
            reasons.append("support_and_contradiction_both_present")

        if self._has_warning(item, ClaimEvaluationWarningType.NEEDS_REVIEW):
            score += 0.2
            reasons.append("needs_review_warning")

        if self._has_warning(item, ClaimEvaluationWarningType.MISSING_PROVENANCE):
            score += 0.15
            reasons.append("missing_provenance")

        if self._has_warning(item, ClaimEvaluationWarningType.SAME_LINEAGE_NOT_CORROBORATION):
            score += 0.12
            reasons.append("same_lineage_repetition")

        if self._has_warning(item, ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION) or self._has_warning(
            item, ClaimEvaluationWarningType.REPORTED_CLAIM_CAUTION
        ):
            score += 0.1
            reasons.append("speculative_or_reported_evidence")

        if any(summary.independence_score < 0.45 for summary in self._all_summaries(item)):
            score += 0.08
            reasons.append("low_source_independence")

        if item.uncertainty_summaries:
            score += 0.08
            reasons.append("uncertainty_visible")

        score = _clamp(score)
        if score >= 0.75:
            return ReviewPriority.URGENT, score, sorted(set(reasons))
        if score >= 0.5:
            return ReviewPriority.HIGH, score, sorted(set(reasons))
        if score >= 0.25:
            return ReviewPriority.MEDIUM, score, sorted(set(reasons))
        return ReviewPriority.LOW, score, sorted(set(reasons))

    def _all_summaries(self, item: ClaimReviewItem) -> list[EvidenceAssessmentSummary]:
        return item.support_summaries + item.contradiction_summaries + item.uncertainty_summaries

    def _has_warning(self, item: ClaimReviewItem, warning_type: ClaimEvaluationWarningType) -> bool:
        return warning_type in item.warning_types
