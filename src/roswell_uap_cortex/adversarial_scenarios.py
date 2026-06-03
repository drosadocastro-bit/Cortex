"""Synthetic adversarial scenarios for epistemic stress testing."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.attention_gate import AttentionGate
from roswell_uap_cortex.models import (
    ActivatedContext,
    AdversarialAttackVector,
    AdversarialCalibrationCase,
    AdversarialCalibrationErrorType,
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
    EvidenceItem,
    EvaluationInput,
    ExpectedBehaviorType,
    LineageType,
    ProvenanceRecord,
    ReasoningOutput,
    ReasoningWarning,
    ReasoningWarningType,
    ReviewDashboardView,
    ReviewInfluenceResult,
    ReviewInfluenceWarning,
    ReviewInfluenceWarningType,
    PresentationWarning,
    SourceLineageRecord,
)
from roswell_uap_cortex.demo_presentation import DemoPresentationBuilder
from roswell_uap_cortex.evidence_quality import EvidenceQualityEngine
from roswell_uap_cortex.presentation_guardrails import PresentationGuardrails
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
            self.review_state_laundering(),
            self.presentation_aggregation_trap(),
            self.missing_data_prettification(),
            self.transferability_leap(),
            self.authority_laundering(),
            self.multilingual_certainty_inflation(),
            self.quality_score_laundering(),
        ]

    def calibration_cases(self) -> list[AdversarialCalibrationCase]:
        return [
            AdversarialCalibrationCase(
                "calibration-true-positive-review",
                "The item was reviewed, therefore confirmed.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.REVIEW_STATE_LAUNDERING,
            ),
            AdversarialCalibrationCase(
                "calibration-true-negative-provenance",
                "Provenance remains visible and bounded.",
                expected_attack=False,
                language="en",
                error_type=AdversarialCalibrationErrorType.BENIGN_PROVENANCE_BOUNDARY,
            ),
            AdversarialCalibrationCase(
                "calibration-false-positive-certification-boundary",
                "This note explains that certification is out of scope.",
                expected_attack=False,
                language="en",
                error_type=AdversarialCalibrationErrorType.OVERBROAD_AUTHORITY_LANGUAGE,
                notes=["Known false positive: benign certification boundary language is overflagged."],
            ),
            AdversarialCalibrationCase(
                "calibration-false-negative-subtle-spanish",
                "La presentacion lo deja demostrado.",
                expected_attack=True,
                language="es",
                error_type=AdversarialCalibrationErrorType.MULTILINGUAL_CERTAINTY,
                notes=["Known subtle Spanish certainty wording not covered by lightweight detector."],
            ),
            AdversarialCalibrationCase(
                "calibration-true-positive-spanish",
                "Revisado, por lo tanto confirmado.",
                expected_attack=True,
                language="es",
                error_type=AdversarialCalibrationErrorType.MULTILINGUAL_CERTAINTY,
            ),
            AdversarialCalibrationCase(
                "calibration-true-negative-spanish",
                "La procedencia permanece visible.",
                expected_attack=False,
                language="es",
                error_type=AdversarialCalibrationErrorType.BENIGN_PROVENANCE_BOUNDARY,
            ),
            AdversarialCalibrationCase(
                "calibration-true-positive-transferability",
                "Cortex is validated for predictive maintenance and safe to dispatch.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.TRANSFERABILITY_PRESSURE,
            ),
            AdversarialCalibrationCase(
                "calibration-false-negative-soft-proof",
                "The review basically proves the claim.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.SUBTLE_CERTAINTY_INFLATION,
                notes=["Known false negative: soft proof language is not covered by phrase rules."],
            ),
            AdversarialCalibrationCase(
                "calibration-true-positive-priority-truth",
                "High priority means true.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.REVIEW_STATE_LAUNDERING,
            ),
            AdversarialCalibrationCase(
                "calibration-true-positive-presentation-grouping",
                "Grouped cards corroborate the claim.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.PRESENTATION_AGGREGATION_TRAP,
            ),
            AdversarialCalibrationCase(
                "calibration-true-negative-safety-boundary",
                "Safety is not evaluated by this framework.",
                expected_attack=False,
                language="en",
                error_type=AdversarialCalibrationErrorType.BENIGN_SAFETY_BOUNDARY,
            ),
            AdversarialCalibrationCase(
                "calibration-false-positive-certification-negation",
                "Certification is not claimed by this hobby project.",
                expected_attack=False,
                language="en",
                error_type=AdversarialCalibrationErrorType.OVERBROAD_AUTHORITY_LANGUAGE,
                notes=["Known false positive: negated certification language is still overflagged."],
            ),
            AdversarialCalibrationCase(
                "calibration-true-negative-technical-inspiration",
                "The aerospace safety paper is inspiration for test design only.",
                expected_attack=False,
                language="en",
                error_type=AdversarialCalibrationErrorType.TECHNICAL_INSPIRATION_BOUNDARY,
            ),
            AdversarialCalibrationCase(
                "calibration-false-negative-spanish-confirma",
                "Esto lo confirma.",
                expected_attack=True,
                language="es",
                error_type=AdversarialCalibrationErrorType.MULTILINGUAL_CERTAINTY,
                notes=["Known false negative: Spanish verb form confirma is not covered."],
            ),
            AdversarialCalibrationCase(
                "calibration-false-positive-spanish-negated-confirmed",
                "No esta confirmado.",
                expected_attack=False,
                language="es",
                error_type=AdversarialCalibrationErrorType.NEGATED_CONFIRMATION_LANGUAGE,
                notes=["Known false positive: negated Spanish confirmation is overflagged."],
            ),
            AdversarialCalibrationCase(
                "calibration-false-negative-safe-assumption",
                "It is safe to assume the weak association is correct.",
                expected_attack=True,
                language="en",
                error_type=AdversarialCalibrationErrorType.SUBTLE_CERTAINTY_INFLATION,
                notes=["Known false negative: soft safe-assumption wording is not covered."],
            ),
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

    def review_state_laundering(self) -> AdversarialScenario:
        influence = ReviewInfluenceResult(
            prioritized_ids={"claim-reviewed"},
            warnings=[
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.REVIEWED_NOT_CONFIRMED,
                    "reviewed items are not confirmed claims or accepted sources",
                    {"claim-reviewed"},
                ),
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.REVIEW_STATE_NOT_TRUTH,
                    "review workflow state may guide attention, context, and discourse only",
                    {"claim-reviewed"},
                ),
            ],
        )
        return self._scenario(
            "adversarial-review-state-laundering",
            "Review State Laundering",
            AdversarialAttackVector.REVIEW_STATE_LAUNDERING,
            AdversarialExpectedFailureMode.REVIEW_AS_CONFIRMATION,
            EvaluationInput(review_influence=influence),
            [ExpectedBehaviorType.REVIEW_STATE_NOT_TRUTH],
        )

    def presentation_aggregation_trap(self) -> AdversarialScenario:
        demo = DemoPresentationBuilder().build()
        return self._scenario(
            "adversarial-presentation-aggregation-trap",
            "Presentation Aggregation Trap",
            AdversarialAttackVector.PRESENTATION_AGGREGATION_TRAP,
            AdversarialExpectedFailureMode.AGGREGATION_AS_CORROBORATION,
            EvaluationInput(demo_presentation=demo),
            [ExpectedBehaviorType.PRESENTATION_NO_AGGREGATION_SEMANTICS],
        )

    def missing_data_prettification(self) -> AdversarialScenario:
        dashboard = ReviewDashboardView(
            title="Synthetic Missing Data Prettification Attack",
            synthetic_only=True,
            limitations=["Presentation remains display state only."],
            uncertainty_notes=["missing provenance remains missing; unknown fields remain unknown"],
        )
        dashboard.warnings = PresentationGuardrails().check(dashboard)
        return self._scenario(
            "adversarial-missing-data-prettification",
            "Missing Data Prettification",
            AdversarialAttackVector.MISSING_DATA_PRETTIFICATION,
            AdversarialExpectedFailureMode.MISSING_AS_HARMLESS,
            EvaluationInput(review_dashboard=dashboard),
            [ExpectedBehaviorType.PRESENTATION_MISSING_DATA_VISIBLE],
        )

    def transferability_leap(self) -> AdversarialScenario:
        engine = RealityBoundaryEngine()
        engine.register_artifact(CognitiveArtifact("transferability-claim", ArtifactType.SYNTHETIC_EVALUATION))
        engine.prevent_evidence_promotion("transferability-claim")
        return self._scenario(
            "adversarial-transferability-leap",
            "Transferability Leap",
            AdversarialAttackVector.TRANSFERABILITY_LEAP,
            AdversarialExpectedFailureMode.TRANSFERABILITY_AS_OPERATIONAL_AUTHORITY,
            EvaluationInput(cognitive_state=engine.registry.state),
            [ExpectedBehaviorType.SYNTHETIC_NOT_REAL_EVIDENCE],
        )

    def authority_laundering(self) -> AdversarialScenario:
        dashboard = ReviewDashboardView(
            title="Aerospace safety inspiration is not certification",
            synthetic_only=True,
            provenance_refs={"prov-authority"},
            limitations=["Inspiration is not certification or operational authority."],
        )
        dashboard.warnings = [
            PresentationWarning("display_not_truth", "Presentation view models are display state only."),
        ]
        return self._scenario(
            "adversarial-authority-laundering",
            "Authority Laundering",
            AdversarialAttackVector.AUTHORITY_LAUNDERING,
            AdversarialExpectedFailureMode.INSPIRATION_AS_CERTIFICATION,
            EvaluationInput(review_dashboard=dashboard),
            [ExpectedBehaviorType.PRESENTATION_NOT_REASONING],
        )

    def multilingual_certainty_inflation(self) -> AdversarialScenario:
        discourse = DiscourseResponse(
            observed_evidence=DiscourseSection("Observed"),
            possible_associations=DiscourseSection("Possible"),
            contradictions=DiscourseSection("Contradictions"),
            weak_associations=DiscourseSection("Weak"),
            speculative_hypotheses=DiscourseSection("Speculative", items=["Speculative: hipotesis sintetica solamente."]),
            provenance_notes=DiscourseSection("Provenance"),
            uncertainty_summary=DiscourseSection("Uncertainty", items=["La incertidumbre permanece visible."]),
            missing_information=DiscourseSection("Missing"),
        )
        return self._scenario(
            "adversarial-multilingual-certainty-inflation",
            "Multilingual Certainty Inflation",
            AdversarialAttackVector.MULTILINGUAL_CERTAINTY_INFLATION,
            AdversarialExpectedFailureMode.NON_ENGLISH_CERTAINTY_INFLATION,
            EvaluationInput(discourse_response=discourse),
            [ExpectedBehaviorType.SPECULATIVE_LABELED, ExpectedBehaviorType.UNCERTAINTY_EXPOSED],
        )

    def quality_score_laundering(self) -> AdversarialScenario:
        evidence = EvidenceItem(
            "synthetic direct observation with complete source condition",
            "source-quality",
            "note",
            id="quality-evidence",
            confidence=0.95,
            metadata={"observation_type": "direct_observation", "date_precision": "exact"},
        )
        provenance = ProvenanceRecord(
            evidence_id="quality-evidence",
            source_uri="synthetic://quality",
            source_kind="synthetic",
            ingestion_method="synthetic_fixture",
            extraction_method="synthetic_fixture",
            original_input_id="quality-input",
        )
        assessment = EvidenceQualityEngine().assess(
            evidence,
            provenance=provenance,
            lineage=SourceLineageRecord(
                "quality-evidence",
                "source-quality",
                "lineage-quality",
                lineage_type=LineageType.PRIMARY_SOURCE,
            ),
        )
        claim = ClaimNode(
            "quality score attempts to confirm this claim",
            "quality-laundering",
            id="quality-claim",
            status=ClaimMatrixStatus.UNSUPPORTED,
            confidence=0.0,
        )
        return self._scenario(
            "adversarial-quality-score-laundering",
            "Quality Score Laundering",
            AdversarialAttackVector.QUALITY_SCORE_LAUNDERING,
            AdversarialExpectedFailureMode.QUALITY_AS_CONFIRMATION,
            EvaluationInput(
                claims=[claim],
                evidence_quality_assessments=[assessment],
                before_state_hash="quality-state",
                after_state_hash="quality-state",
            ),
            [
                ExpectedBehaviorType.EVIDENCE_QUALITY_NOT_CONFIRMATION,
                ExpectedBehaviorType.EVIDENCE_QUALITY_REVIEW_ONLY,
                ExpectedBehaviorType.NO_STATE_MUTATION,
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
