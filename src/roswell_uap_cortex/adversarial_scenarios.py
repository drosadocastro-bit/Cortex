"""Synthetic adversarial scenarios for epistemic stress testing."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.attention_gate import AttentionGate
from roswell_uap_cortex.models import (
    ActivatedContext,
    AdversarialAttackVector,
    AdversarialExpectedFailureMode,
    AdversarialScenario,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    ArtifactType,
    AttentionCandidate,
    ClaimMatrixStatus,
    ClaimNode,
    CognitiveArtifact,
    DiscourseCitation,
    DiscourseResponse,
    DiscourseSection,
    EvaluationInput,
    ExpectedBehaviorType,
    ReasoningOutput,
    ReasoningWarning,
    ReasoningWarningType,
    SourceLineageRecord,
)
from roswell_uap_cortex.reality_boundary import RealityBoundaryEngine


@dataclass(slots=True)
class AdversarialScenarioFactory:
    """Create tiny synthetic attacks; none are real-world claims."""

    def all(self) -> list[AdversarialScenario]:
        return [
            self.provenance_laundering(),
            self.semantic_echo_chamber(),
            self.discourse_contamination(),
            self.confidence_inflation(),
            self.contradiction_suppression(),
            self.speculation_hardening(),
            self.synthetic_to_real_confusion(),
            self.missing_provenance_camouflage(),
            self.temporal_overreach(),
            self.policy_abuse(),
        ]

    def provenance_laundering(self) -> AdversarialScenario:
        reasoning = ReasoningOutput(
            reasoning_warnings=[
                ReasoningWarning(
                    ReasoningWarningType.SAME_LINEAGE_REPETITION,
                    "Repeated same-lineage evidence is not independent.",
                    {"e1", "e2", "e3"},
                )
            ]
        )
        lineage = [
            SourceLineageRecord("e1", "s1", "laundered"),
            SourceLineageRecord("e2", "s2", "laundered"),
            SourceLineageRecord("e3", "s3", "laundered"),
        ]
        return self._scenario(
            "adversarial-provenance-laundering",
            "Provenance Laundering",
            AdversarialAttackVector.PROVENANCE_LAUNDERING,
            AdversarialExpectedFailureMode.FALSE_INDEPENDENCE,
            EvaluationInput(reasoning_output=reasoning, lineage_records=lineage),
            [ExpectedBehaviorType.SAME_LINEAGE_NOT_INDEPENDENT],
        )

    def semantic_echo_chamber(self) -> AdversarialScenario:
        return self._scenario(
            "adversarial-semantic-echo-chamber",
            "Semantic Echo Chamber",
            AdversarialAttackVector.SEMANTIC_ECHO_CHAMBER,
            AdversarialExpectedFailureMode.SIMILARITY_AS_CONFIRMATION,
            EvaluationInput(before_state_hash="semantic-echo", after_state_hash="semantic-echo"),
            [
                ExpectedBehaviorType.NO_STATE_MUTATION,
                ExpectedBehaviorType.SEMANTIC_LINEAGE_ECHO_DOWNGRADED,
                ExpectedBehaviorType.SEMANTIC_SIMILARITY_NOT_CONFIRMATION,
            ],
        )

    def discourse_contamination(self) -> AdversarialScenario:
        engine = RealityBoundaryEngine()
        engine.register_artifact(
            CognitiveArtifact(
                "discourse-as-evidence",
                ArtifactType.DISCOURSE_OUTPUT,
                provenance_ids={"prov"},
                layer_origin="adversarial_discourse",
            )
        )
        engine.prevent_evidence_promotion("discourse-as-evidence")
        return self._scenario(
            "adversarial-discourse-contamination",
            "Discourse Contamination",
            AdversarialAttackVector.DISCOURSE_CONTAMINATION,
            AdversarialExpectedFailureMode.DISCOURSE_AS_EVIDENCE,
            EvaluationInput(cognitive_state=engine.registry.state),
            [ExpectedBehaviorType.DISCOURSE_NOT_EVIDENCE],
        )

    def confidence_inflation(self) -> AdversarialScenario:
        claims = [ClaimNode("weak repeated claim", "topic", status=ClaimMatrixStatus.UNSUPPORTED)]
        discourse = DiscourseResponse(
            observed_evidence=DiscourseSection("Observed"),
            possible_associations=DiscourseSection("Possible"),
            contradictions=DiscourseSection("Contradictions"),
            weak_associations=DiscourseSection("Weak"),
            speculative_hypotheses=DiscourseSection("Speculative"),
            provenance_notes=DiscourseSection("Provenance"),
            uncertainty_summary=DiscourseSection("Uncertainty", items=["Unsupported claim remains unsupported."]),
            missing_information=DiscourseSection("Missing"),
        )
        return self._scenario(
            "adversarial-confidence-inflation",
            "Confidence Inflation",
            AdversarialAttackVector.CONFIDENCE_INFLATION,
            AdversarialExpectedFailureMode.UNSUPPORTED_CONFIDENCE_INFLATION,
            EvaluationInput(claims=claims, discourse_response=discourse),
            [ExpectedBehaviorType.UNSUPPORTED_CLAIM_NOT_CONFIRMED],
        )

    def contradiction_suppression(self) -> AdversarialScenario:
        reasoning = ReasoningOutput(contested_context_ids={"claim-a", "claim-b"})
        discourse = DiscourseResponse(
            observed_evidence=DiscourseSection("Observed"),
            possible_associations=DiscourseSection("Possible"),
            contradictions=DiscourseSection("Contradictions", items=["claim-a conflicts with claim-b"]),
            weak_associations=DiscourseSection("Weak"),
            speculative_hypotheses=DiscourseSection("Speculative"),
            provenance_notes=DiscourseSection("Provenance"),
            uncertainty_summary=DiscourseSection("Uncertainty"),
            missing_information=DiscourseSection("Missing"),
        )
        return self._scenario(
            "adversarial-contradiction-suppression",
            "Contradiction Suppression",
            AdversarialAttackVector.CONTRADICTION_SUPPRESSION,
            AdversarialExpectedFailureMode.HIDDEN_CONTRADICTION,
            EvaluationInput(reasoning_output=reasoning, discourse_response=discourse),
            [ExpectedBehaviorType.CONTRADICTIONS_PRESERVED],
        )

    def speculation_hardening(self) -> AdversarialScenario:
        discourse = DiscourseResponse(
            observed_evidence=DiscourseSection("Observed"),
            possible_associations=DiscourseSection("Possible"),
            contradictions=DiscourseSection("Contradictions"),
            weak_associations=DiscourseSection("Weak"),
            speculative_hypotheses=DiscourseSection("Speculative", items=["Speculative: synthetic hypothesis only."]),
            provenance_notes=DiscourseSection("Provenance"),
            uncertainty_summary=DiscourseSection("Uncertainty"),
            missing_information=DiscourseSection("Missing"),
        )
        return self._scenario(
            "adversarial-speculation-hardening",
            "Speculation Hardening",
            AdversarialAttackVector.SPECULATION_HARDENING,
            AdversarialExpectedFailureMode.SPECULATION_AS_FACT,
            EvaluationInput(discourse_response=discourse),
            [ExpectedBehaviorType.SPECULATIVE_LABELED],
        )

    def synthetic_to_real_confusion(self) -> AdversarialScenario:
        engine = RealityBoundaryEngine()
        engine.register_artifact(CognitiveArtifact("eval", ArtifactType.SYNTHETIC_EVALUATION))
        engine.prevent_evidence_promotion("eval")
        return self._scenario(
            "adversarial-synthetic-to-real",
            "Synthetic To Real Confusion",
            AdversarialAttackVector.SYNTHETIC_TO_REAL_CONFUSION,
            AdversarialExpectedFailureMode.SYNTHETIC_AS_REAL_EVIDENCE,
            EvaluationInput(cognitive_state=engine.registry.state),
            [ExpectedBehaviorType.SYNTHETIC_NOT_REAL_EVIDENCE],
        )

    def missing_provenance_camouflage(self) -> AdversarialScenario:
        decision = AttentionGate().apply(
            [
                AttentionCandidate(
                    "camouflage",
                    "evidence",
                    text="rich synthetic metadata but no provenance",
                    provenance_ids=set(),
                    metadata={"author": "synthetic", "detail": "dense"},
                )
            ],
            policy="provenance_first",
        )
        return self._scenario(
            "adversarial-missing-provenance-camouflage",
            "Missing Provenance Camouflage",
            AdversarialAttackVector.MISSING_PROVENANCE_CAMOUFLAGE,
            AdversarialExpectedFailureMode.PROVENANCE_GAP_HIDDEN,
            EvaluationInput(attention_decision=decision),
            [ExpectedBehaviorType.ATTENTION_PROVENANCE_WARNING_VISIBLE],
        )

    def temporal_overreach(self) -> AdversarialScenario:
        return self._scenario(
            "adversarial-temporal-overreach",
            "Temporal Overreach",
            AdversarialAttackVector.TEMPORAL_OVERREACH,
            AdversarialExpectedFailureMode.FABRICATED_TEMPORAL_PRECISION,
            EvaluationInput(before_state_hash="temporal-unknown", after_state_hash="temporal-unknown"),
            [ExpectedBehaviorType.NO_STATE_MUTATION],
        )

    def policy_abuse(self) -> AdversarialScenario:
        decision = AttentionGate().apply(
            [
                AttentionCandidate("dirty", "evidence", provenance_ids={"prov"}, contamination_risk=0.9),
                AttentionCandidate("contradictory", "claim", provenance_ids={"prov"}, contradiction_pressure=0.8, contested=True),
            ],
            policy="exploratory",
        )
        return self._scenario(
            "adversarial-policy-abuse",
            "Policy Abuse",
            AdversarialAttackVector.POLICY_ABUSE,
            AdversarialExpectedFailureMode.GUARDRAIL_DISABLED_BY_POLICY,
            EvaluationInput(attention_decision=decision),
            [
                ExpectedBehaviorType.ATTENTION_CONTAMINATION_WARNING_VISIBLE,
                ExpectedBehaviorType.ATTENTION_CONTRADICTION_VISIBLE,
            ],
        )

    def _scenario(
        self,
        scenario_id: str,
        title: str,
        attack_vector: AdversarialAttackVector,
        failure_mode: AdversarialExpectedFailureMode,
        inputs: EvaluationInput,
        behaviors: list[ExpectedBehaviorType],
    ) -> AdversarialScenario:
        return AdversarialScenario(
            scenario_id=scenario_id,
            title=title,
            attack_vector=attack_vector,
            expected_failure_mode=failure_mode,
            description="Synthetic adversarial stress test for framework guardrails only.",
            inputs=inputs,
            expected_behaviors=behaviors,
            tags={"synthetic", "adversarial", attack_vector.value},
        )
