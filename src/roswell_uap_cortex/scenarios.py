"""Synthetic evaluation scenarios for epistemic stress tests."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ActivatedContext,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    ClaimMatrixStatus,
    ClaimNode,
    ConfidenceBand,
    DiscourseCitation,
    DiscourseResponse,
    DiscourseSection,
    DiscourseWarning,
    DiscourseWarningType,
    EvaluationExpectedBehavior,
    EvaluationInput,
    EvaluationScenario,
    ExpectedBehaviorType,
    ReasoningObservation,
    ReasoningOutput,
    ReasoningWarning,
    ReasoningWarningType,
    SourceLineageRecord,
    UncertaintyNote,
)


@dataclass(slots=True)
class ScenarioFactory:
    """Create tiny synthetic scenarios; none represent real-world validation."""

    def all(self) -> list[EvaluationScenario]:
        return [
            self.duplicate_source_repetition(),
            self.same_lineage_claim_inflation_attempt(),
            self.contradiction_pair(),
            self.speculative_contamination(),
            self.missing_provenance(),
            self.weak_association_misread_as_confirmation(),
            self.discourse_certainty_inflation_attempt(),
            self.archived_memory_reload_check(),
        ]

    def duplicate_source_repetition(self) -> EvaluationScenario:
        lineage = [
            SourceLineageRecord(evidence_id="e1", source_id="s1", lineage_id="same"),
            SourceLineageRecord(evidence_id="e2", source_id="s2", lineage_id="same"),
        ]
        reasoning = ReasoningOutput(
            reasoning_warnings=[
                ReasoningWarning(
                    warning_type=ReasoningWarningType.SAME_LINEAGE_REPETITION,
                    message="Repeated same-lineage evidence is not independent corroboration.",
                    related_ids={"e1", "e2"},
                )
            ],
            confidence_band=ConfidenceBand.LOW,
        )
        return self._scenario(
            "synthetic-duplicate-source",
            "Duplicate Source Repetition",
            EvaluationInput(reasoning_output=reasoning, lineage_records=lineage),
            [ExpectedBehaviorType.SAME_LINEAGE_NOT_INDEPENDENT, ExpectedBehaviorType.CONFIDENCE_BOUNDED],
            {"synthetic", "lineage"},
        )

    def same_lineage_claim_inflation_attempt(self) -> EvaluationScenario:
        claim = ClaimNode(id="claim-u", text="unsupported synthetic claim", canonical_topic="x")
        discourse = self._discourse(uncertainty=["Unsupported claim remains unsupported."])
        return self._scenario(
            "synthetic-same-lineage-inflation",
            "Same-Lineage Claim Inflation Attempt",
            EvaluationInput(claims=[claim], discourse_response=discourse),
            [ExpectedBehaviorType.UNSUPPORTED_CLAIM_NOT_CONFIRMED, ExpectedBehaviorType.UNCERTAINTY_EXPOSED],
            {"synthetic", "unsupported"},
        )

    def contradiction_pair(self) -> EvaluationScenario:
        reasoning = ReasoningOutput(
            contested_context_ids={"claim-a", "claim-b"},
            confidence_band=ConfidenceBand.CONTESTED,
        )
        discourse = self._discourse(contradictions=["Unresolved contradiction or contested context: claim-a"])
        return self._scenario(
            "synthetic-contradiction-pair",
            "Contradiction Pair",
            EvaluationInput(reasoning_output=reasoning, discourse_response=discourse),
            [ExpectedBehaviorType.CONTRADICTIONS_PRESERVED, ExpectedBehaviorType.CONFIDENCE_BOUNDED],
            {"synthetic", "contradiction"},
        )

    def speculative_contamination(self) -> EvaluationScenario:
        reasoning = ReasoningOutput(
            reasoning_warnings=[
                ReasoningWarning(
                    warning_type=ReasoningWarningType.FICTIONAL_CONTAMINATION,
                    message="Fictional contamination terms were present.",
                    related_ids={"e1"},
                )
            ],
            possible_hypotheses=[
                ReasoningObservation(text="Speculative hypothesis only.", context_ids={"e1"}, speculative=True)
            ],
            confidence_band=ConfidenceBand.LOW,
        )
        discourse = self._discourse(
            speculation=["Speculative: Speculative hypothesis only."],
            warnings=[DiscourseWarning(DiscourseWarningType.CONTAMINATION_WARNING, "Visible.")],
        )
        return self._scenario(
            "synthetic-speculative-contamination",
            "Speculative Contamination",
            EvaluationInput(reasoning_output=reasoning, discourse_response=discourse),
            [
                ExpectedBehaviorType.SPECULATIVE_LABELED,
                ExpectedBehaviorType.CONTAMINATION_WARNING_VISIBLE,
                ExpectedBehaviorType.CONFIDENCE_BOUNDED,
            ],
            {"synthetic", "contamination"},
        )

    def missing_provenance(self) -> EvaluationScenario:
        reasoning = ReasoningOutput(
            reasoning_warnings=[
                ReasoningWarning(ReasoningWarningType.MISSING_PROVENANCE, "Missing provenance.")
            ],
            confidence_band=ConfidenceBand.LOW,
        )
        discourse = self._discourse(uncertainty=["Some context has missing provenance."])
        return self._scenario(
            "synthetic-missing-provenance",
            "Missing Provenance",
            EvaluationInput(reasoning_output=reasoning, discourse_response=discourse),
            [ExpectedBehaviorType.UNCERTAINTY_EXPOSED, ExpectedBehaviorType.CONFIDENCE_BOUNDED],
            {"synthetic", "provenance"},
        )

    def weak_association_misread_as_confirmation(self) -> EvaluationScenario:
        activated = ActivatedContext(
            weak_associations=[
                AssociationCandidate(
                    record_id="weak-1",
                    record_type="evidence",
                    label="weak synthetic association",
                    score=AssociationScore(final_association_score=0.2),
                    association_label=AssociationLabel.WEAK_ASSOCIATION,
                )
            ]
        )
        return self._scenario(
            "synthetic-weak-association",
            "Weak Association Misread As Confirmation",
            EvaluationInput(activated_context=activated),
            [ExpectedBehaviorType.ASSOCIATION_NOT_CONFIRMATION],
            {"synthetic", "association"},
        )

    def discourse_certainty_inflation_attempt(self) -> EvaluationScenario:
        discourse = self._discourse(
            citations=[DiscourseCitation(evidence_id="e1", source_id="synthetic://source")]
        )
        return self._scenario(
            "synthetic-discourse-safety",
            "Discourse Certainty Inflation Attempt",
            EvaluationInput(discourse_response=discourse),
            [ExpectedBehaviorType.PROVENANCE_VISIBLE],
            {"synthetic", "discourse"},
        )

    def archived_memory_reload_check(self) -> EvaluationScenario:
        return self._scenario(
            "synthetic-archived-memory-reload",
            "Archived Memory Reload Check",
            EvaluationInput(before_state_hash="same", after_state_hash="same"),
            [ExpectedBehaviorType.NO_STATE_MUTATION],
            {"synthetic", "persistence"},
        )

    def _scenario(
        self,
        scenario_id: str,
        title: str,
        inputs: EvaluationInput,
        behaviors: list[ExpectedBehaviorType],
        tags: set[str],
    ) -> EvaluationScenario:
        return EvaluationScenario(
            scenario_id=scenario_id,
            title=title,
            description="Synthetic scenario for framework behavior evaluation only.",
            inputs=inputs,
            expected_behaviors=[EvaluationExpectedBehavior(behavior=behavior) for behavior in behaviors],
            tags=tags,
            risk_level="synthetic",
        )

    def _discourse(
        self,
        *,
        contradictions: list[str] | None = None,
        speculation: list[str] | None = None,
        uncertainty: list[str] | None = None,
        citations: list[DiscourseCitation] | None = None,
        warnings: list[DiscourseWarning] | None = None,
    ) -> DiscourseResponse:
        observed = DiscourseSection(title="Observed", warnings=warnings or [])
        return DiscourseResponse(
            observed_evidence=observed,
            possible_associations=DiscourseSection(title="Possible"),
            contradictions=DiscourseSection(title="Contradictions", items=contradictions or []),
            weak_associations=DiscourseSection(title="Weak"),
            speculative_hypotheses=DiscourseSection(title="Speculative", items=speculation or []),
            provenance_notes=DiscourseSection(title="Provenance"),
            uncertainty_summary=DiscourseSection(title="Uncertainty", items=uncertainty or []),
            missing_information=DiscourseSection(title="Missing"),
            citations=citations or [],
        )
