"""Deterministic epistemic metrics for synthetic evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import EvaluationMetric, EvaluationResult, ExpectedBehaviorType


@dataclass(slots=True)
class EpistemicMetrics:
    """Compute bounded framework-behavior metrics, not truth metrics."""

    def summarize(self, results: list[EvaluationResult]) -> list[EvaluationMetric]:
        metric_map = {
            "provenance_visibility_rate": ExpectedBehaviorType.PROVENANCE_VISIBLE,
            "contradiction_preservation_rate": ExpectedBehaviorType.CONTRADICTIONS_PRESERVED,
            "unsupported_claim_suppression_rate": ExpectedBehaviorType.UNSUPPORTED_CLAIM_NOT_CONFIRMED,
            "association_confirmation_separation_rate": ExpectedBehaviorType.ASSOCIATION_NOT_CONFIRMATION,
            "lineage_contamination_detection_rate": ExpectedBehaviorType.SAME_LINEAGE_NOT_INDEPENDENT,
            "uncertainty_exposure_rate": ExpectedBehaviorType.UNCERTAINTY_EXPOSED,
            "contamination_warning_rate": ExpectedBehaviorType.CONTAMINATION_WARNING_VISIBLE,
            "bounded_confidence_rate": ExpectedBehaviorType.CONFIDENCE_BOUNDED,
            "no_mutation_rate": ExpectedBehaviorType.NO_STATE_MUTATION,
            "review_state_boundary_rate": ExpectedBehaviorType.REVIEW_STATE_NOT_TRUTH,
            "presentation_boundary_rate": ExpectedBehaviorType.PRESENTATION_NOT_REASONING,
            "synthetic_demo_presentation_rate": ExpectedBehaviorType.DEMO_PRESENTATION_SYNTHETIC_ONLY,
        }
        return [
            EvaluationMetric(name=name, value=self.rate(results, behavior))
            for name, behavior in metric_map.items()
        ]

    def rate(self, results: list[EvaluationResult], behavior: ExpectedBehaviorType) -> float:
        relevant = [result for result in results if behavior in result.behavior_results]
        if not relevant:
            return 0.0
        passed = sum(1 for result in relevant if result.behavior_results[behavior])
        return passed / len(relevant)
