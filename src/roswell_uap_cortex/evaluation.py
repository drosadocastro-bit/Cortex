"""Deterministic evaluation harness for epistemic guardrails."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.evaluation_guardrails import EvaluationGuardrails
from roswell_uap_cortex.metrics import EpistemicMetrics
from roswell_uap_cortex.models import (
    AssociationLabel,
    ClaimMatrixStatus,
    ConfidenceBand,
    DiscourseWarningType,
    EvaluationFailure,
    EvaluationReport,
    EvaluationResult,
    EvaluationScenario,
    ExpectedBehaviorType,
    ReasoningWarningType,
)


@dataclass(slots=True)
class EvaluationHarness:
    """Run deterministic checks against synthetic scenario artifacts."""

    metrics: EpistemicMetrics = field(default_factory=EpistemicMetrics)
    guardrails: EvaluationGuardrails = field(default_factory=EvaluationGuardrails)

    def run(self, scenarios: list[EvaluationScenario]) -> EvaluationReport:
        results = [self.evaluate(scenario) for scenario in scenarios]
        metric_values = self.metrics.summarize(results)
        total_behaviors = sum(len(result.behavior_results) for result in results)
        passed_behaviors = sum(
            1 for result in results for passed in result.behavior_results.values() if passed
        )
        pass_rate = 0.0 if total_behaviors == 0 else passed_behaviors / total_behaviors
        return EvaluationReport(
            results=results,
            metrics=metric_values,
            limitations=self.guardrails.limitations(),
            overall_pass_rate=pass_rate,
        )

    def evaluate(self, scenario: EvaluationScenario) -> EvaluationResult:
        result = EvaluationResult(scenario_id=scenario.scenario_id)
        for expected in scenario.expected_behaviors:
            passed, message, related_ids = self._check(expected.behavior, scenario)
            result.behavior_results[expected.behavior] = passed
            if not passed:
                result.failures.append(
                    EvaluationFailure(
                        scenario_id=scenario.scenario_id,
                        behavior=expected.behavior,
                        message=message,
                        related_ids=related_ids,
                    )
                )
        return result

    def _check(
        self,
        behavior: ExpectedBehaviorType,
        scenario: EvaluationScenario,
    ) -> tuple[bool, str, set[str]]:
        inputs = scenario.inputs
        discourse = inputs.discourse_response
        reasoning = inputs.reasoning_output
        activated = inputs.activated_context

        if behavior is ExpectedBehaviorType.PROVENANCE_VISIBLE:
            passed = bool(discourse and discourse.citations)
            return passed, "provenance citations missing", set()
        if behavior is ExpectedBehaviorType.CONTRADICTIONS_PRESERVED:
            passed = bool(
                (discourse and discourse.contradictions.items)
                or (reasoning and reasoning.contested_context_ids)
            )
            return passed, "contradictions were not preserved", set()
        if behavior is ExpectedBehaviorType.UNSUPPORTED_CLAIM_NOT_CONFIRMED:
            unsupported = [claim for claim in inputs.claims if claim.status is ClaimMatrixStatus.UNSUPPORTED]
            narrative = "" if not discourse else " ".join(
                [
                    discourse.narrative.observations,
                    discourse.narrative.interpretations,
                    discourse.narrative.speculation,
                    discourse.narrative.uncertainty,
                ]
            ).casefold()
            passed = bool(unsupported) and not any(
                term in narrative for term in ("confirmed", "proves", "definitely")
            )
            return passed, "unsupported claim appeared confirmed", {claim.id for claim in unsupported}
        if behavior is ExpectedBehaviorType.ASSOCIATION_NOT_CONFIRMATION:
            candidates = []
            if activated:
                candidates = activated.weak_associations + activated.contested_associations
            passed = bool(candidates) and all(
                candidate.association_label
                in {
                    AssociationLabel.POSSIBLE_ASSOCIATION,
                    AssociationLabel.WEAK_ASSOCIATION,
                    AssociationLabel.CONTESTED_ASSOCIATION,
                }
                for candidate in candidates
            )
            return passed, "association was not kept separate from confirmation", set()
        if behavior is ExpectedBehaviorType.SPECULATIVE_LABELED:
            passed = bool(
                discourse
                and discourse.speculative_hypotheses.items
                and all("speculative" in item.casefold() for item in discourse.speculative_hypotheses.items)
            )
            return passed, "speculation was not labeled", set()
        if behavior is ExpectedBehaviorType.SAME_LINEAGE_NOT_INDEPENDENT:
            lineage_counts: dict[str, int] = {}
            for record in inputs.lineage_records:
                lineage_counts[record.lineage_id] = lineage_counts.get(record.lineage_id, 0) + 1
            repeated = {lineage for lineage, count in lineage_counts.items() if count > 1}
            warning_visible = bool(
                reasoning
                and any(
                    warning.warning_type is ReasoningWarningType.SAME_LINEAGE_REPETITION
                    for warning in reasoning.reasoning_warnings
                )
            )
            return bool(repeated and warning_visible), "same-lineage repetition not detected", repeated
        if behavior is ExpectedBehaviorType.UNCERTAINTY_EXPOSED:
            passed = bool(
                (discourse and discourse.uncertainty_summary.items)
                or (reasoning and reasoning.uncertainty_notes)
            )
            return passed, "uncertainty was not exposed", set()
        if behavior is ExpectedBehaviorType.CONTAMINATION_WARNING_VISIBLE:
            passed = bool(
                (reasoning and any(
                    warning.warning_type is ReasoningWarningType.FICTIONAL_CONTAMINATION
                    for warning in reasoning.reasoning_warnings
                ))
                or (discourse and any(
                    warning.warning_type is DiscourseWarningType.CONTAMINATION_WARNING
                    for warning in discourse.observed_evidence.warnings
                ))
            )
            return passed, "contamination warning was not visible", set()
        if behavior is ExpectedBehaviorType.CONFIDENCE_BOUNDED:
            passed = bool(reasoning and reasoning.confidence_band in set(ConfidenceBand))
            return passed, "confidence band was not bounded", set()
        if behavior is ExpectedBehaviorType.NO_STATE_MUTATION:
            passed = inputs.before_state_hash is not None and inputs.before_state_hash == inputs.after_state_hash
            return passed, "state hash changed during evaluation", set()
        return False, "unknown expected behavior", set()
