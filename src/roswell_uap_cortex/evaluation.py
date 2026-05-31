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
        if behavior is ExpectedBehaviorType.ATTENTION_SALIENCE_NOT_CONFIDENCE:
            decision = inputs.attention_decision
            passed = bool(
                decision
                and decision.salience_by_id
                and all(0.0 <= score.final_salience_score <= 1.0 for score in decision.salience_by_id.values())
            )
            return passed, "attention salience was not bounded review priority", set()
        if behavior is ExpectedBehaviorType.ATTENTION_CONTRADICTION_VISIBLE:
            decision = inputs.attention_decision
            passed = bool(
                decision
                and any(candidate.contested or candidate.contradiction_pressure > 0 for candidate in decision.selected_for_review)
            )
            return passed, "contradictory attention candidate was not preserved", set()
        if behavior is ExpectedBehaviorType.ATTENTION_PROVENANCE_WARNING_VISIBLE:
            decision = inputs.attention_decision
            passed = bool(
                decision
                and any(not candidate.provenance_ids for candidate in decision.selected_for_review)
            )
            return passed, "fragile provenance was not escalated for review", set()
        if behavior is ExpectedBehaviorType.ATTENTION_CONTAMINATION_WARNING_VISIBLE:
            decision = inputs.attention_decision
            passed = bool(
                decision
                and any(candidate.contamination_risk > 0 for candidate in decision.selected_for_review)
            )
            return passed, "contaminated salient record was not visible for review", set()
        if behavior is ExpectedBehaviorType.ATTENTION_SAME_LINEAGE_SUPPRESSED:
            decision = inputs.attention_decision
            passed = bool(
                decision
                and any("same_lineage_downgraded" in score.reason_codes for score in decision.salience_by_id.values())
            )
            return passed, "same-lineage attention repetition was not downgraded", set()
        if behavior is ExpectedBehaviorType.CLAIM_NORMALIZATION_NOT_VALIDATION:
            normalized = inputs.normalized_claims
            passed = bool(normalized) and all(claim.confidence == 0.0 for claim in normalized)
            return passed, "claim normalization appeared to create confidence", set()
        if behavior is ExpectedBehaviorType.NORMALIZED_CLAIMS_UNSUPPORTED:
            normalized = inputs.normalized_claims
            passed = bool(normalized) and all(claim.unsupported for claim in normalized)
            return passed, "normalized claims were not kept unsupported", set()
        if behavior in {
            ExpectedBehaviorType.SEMANTIC_SIMILARITY_NOT_CONFIRMATION,
            ExpectedBehaviorType.SEMANTIC_LINEAGE_ECHO_DOWNGRADED,
            ExpectedBehaviorType.SEMANTIC_MISSING_PROVENANCE_WARNING,
            ExpectedBehaviorType.CONTESTED_SEMANTIC_CLUSTER_VISIBLE,
        }:
            passed = inputs.before_state_hash is not None and inputs.before_state_hash == inputs.after_state_hash
            return passed, f"{behavior.value} guardrail did not hold", set()
        if behavior in {
            ExpectedBehaviorType.DISCOURSE_NOT_EVIDENCE,
            ExpectedBehaviorType.REASONING_NOT_CLAIM_MUTATION,
            ExpectedBehaviorType.SEMANTIC_CLUSTER_NOT_GRAPH_SUPPORT,
            ExpectedBehaviorType.SYNTHETIC_NOT_REAL_EVIDENCE,
            ExpectedBehaviorType.SPECULATION_REMAINS_SPECULATION,
        }:
            state = inputs.cognitive_state
            passed = bool(
                state
                and any(violation.violation_type == behavior.value for violation in state.violations)
            )
            return passed, f"{behavior.value} was not blocked", set()
        if behavior is ExpectedBehaviorType.RECURSIVE_INFERENCE_DETECTED:
            state = inputs.cognitive_state
            passed = bool(state and state.warnings)
            return passed, "recursive inference warning missing", set()
        return False, "unknown expected behavior", set()
