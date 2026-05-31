"""Synthetic evaluation scenarios for epistemic stress tests."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ActivatedContext,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    ArtifactType,
    AttentionCandidate,
    AttentionDecision,
    CandidateClaimOrigin,
    ClaimCanonicalKey,
    ClaimMatrixStatus,
    ClaimNode,
    CognitiveArtifact,
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
    NormalizedClaim,
    SourceLineageRecord,
    UncertaintyNote,
)
from roswell_uap_cortex.attention_gate import AttentionGate
from roswell_uap_cortex.reality_boundary import RealityBoundaryEngine


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
            *self.graph_infrastructure_scenarios(),
            *self.semantic_scenarios(),
            *self.reality_boundary_scenarios(),
            *self.attention_scenarios(),
            *self.claim_normalization_scenarios(),
        ]

    def graph_infrastructure_scenarios(self) -> list[EvaluationScenario]:
        """Synthetic graph upgrade checks for traversal and temporal ambiguity boundaries."""
        return [
            self._scenario(
                "synthetic-graph-contradiction-traversal",
                "Graph Contradiction Traversal",
                EvaluationInput(before_state_hash="graph", after_state_hash="graph"),
                [ExpectedBehaviorType.NO_STATE_MUTATION],
                {"synthetic", "graph", "contradiction"},
            ),
            self._scenario(
                "synthetic-graph-lineage-path",
                "Graph Lineage Path Traversal",
                EvaluationInput(before_state_hash="lineage", after_state_hash="lineage"),
                [ExpectedBehaviorType.NO_STATE_MUTATION],
                {"synthetic", "graph", "lineage"},
            ),
            self._scenario(
                "synthetic-temporal-ambiguity",
                "Temporal Ambiguity Preservation",
                EvaluationInput(before_state_hash="temporal", after_state_hash="temporal"),
                [ExpectedBehaviorType.NO_STATE_MUTATION],
                {"synthetic", "temporal", "ambiguity"},
            ),
            self._scenario(
                "synthetic-graph-subgraph-determinism",
                "Deterministic Subgraph Extraction",
                EvaluationInput(before_state_hash="subgraph", after_state_hash="subgraph"),
                [ExpectedBehaviorType.NO_STATE_MUTATION],
                {"synthetic", "graph", "subgraph"},
            ),
            self._scenario(
                "synthetic-graph-duplicate-edge-deduplication",
                "Duplicate Edge Deduplication",
                EvaluationInput(before_state_hash="dedupe", after_state_hash="dedupe"),
                [ExpectedBehaviorType.NO_STATE_MUTATION],
                {"synthetic", "graph", "dedupe"},
            ),
        ]

    def semantic_scenarios(self) -> list[EvaluationScenario]:
        return [
            self._scenario(
                "synthetic-semantic-no-confirmation",
                "Semantic Similarity Without Confirmation",
                EvaluationInput(before_state_hash="semantic", after_state_hash="semantic"),
                [
                    ExpectedBehaviorType.NO_STATE_MUTATION,
                    ExpectedBehaviorType.SEMANTIC_SIMILARITY_NOT_CONFIRMATION,
                ],
                {"synthetic", "semantic"},
            ),
            self._scenario(
                "synthetic-semantic-lineage-echo",
                "Same-Lineage Semantic Echo",
                EvaluationInput(before_state_hash="semantic-lineage", after_state_hash="semantic-lineage"),
                [
                    ExpectedBehaviorType.NO_STATE_MUTATION,
                    ExpectedBehaviorType.SEMANTIC_LINEAGE_ECHO_DOWNGRADED,
                ],
                {"synthetic", "semantic", "lineage"},
            ),
            self._scenario(
                "synthetic-semantic-missing-provenance",
                "High Similarity With Missing Provenance",
                EvaluationInput(before_state_hash="semantic-provenance", after_state_hash="semantic-provenance"),
                [
                    ExpectedBehaviorType.NO_STATE_MUTATION,
                    ExpectedBehaviorType.SEMANTIC_MISSING_PROVENANCE_WARNING,
                ],
                {"synthetic", "semantic", "provenance"},
            ),
            self._scenario(
                "synthetic-contested-semantic-cluster",
                "Contested Semantic Cluster",
                EvaluationInput(before_state_hash="semantic-cluster", after_state_hash="semantic-cluster"),
                [
                    ExpectedBehaviorType.NO_STATE_MUTATION,
                    ExpectedBehaviorType.CONTESTED_SEMANTIC_CLUSTER_VISIBLE,
                ],
                {"synthetic", "semantic", "cluster"},
            ),
        ]

    def reality_boundary_scenarios(self) -> list[EvaluationScenario]:
        return [
            self._boundary_scenario(
                "synthetic-recursive-discourse-contamination",
                "Recursive Discourse Contamination",
                CognitiveArtifact(
                    "discursive-evidence",
                    ArtifactType.DISCOURSE_OUTPUT,
                    source_artifact_ids={"discursive-evidence"},
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_discourse",
                ),
                ExpectedBehaviorType.DISCOURSE_NOT_EVIDENCE,
                {"synthetic", "reality-boundary", "discourse"},
            ),
            self._boundary_scenario(
                "synthetic-self-citation-loop",
                "Self-Citation Loop Attempt",
                CognitiveArtifact(
                    "self-loop",
                    ArtifactType.REASONING_OUTPUT,
                    source_artifact_ids={"self-loop"},
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_reasoning",
                ),
                ExpectedBehaviorType.RECURSIVE_INFERENCE_DETECTED,
                {"synthetic", "reality-boundary", "recursion"},
            ),
            self._boundary_scenario(
                "synthetic-semantic-recursion-loop",
                "Semantic Recursion Loop",
                CognitiveArtifact(
                    "semantic-loop",
                    ArtifactType.SEMANTIC_CLUSTER,
                    source_artifact_ids={"semantic-loop"},
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_semantic",
                ),
                ExpectedBehaviorType.SEMANTIC_CLUSTER_NOT_GRAPH_SUPPORT,
                {"synthetic", "reality-boundary", "semantic"},
            ),
            self._boundary_scenario(
                "synthetic-reasoning-promotion",
                "Reasoning-Output Promotion Attempt",
                CognitiveArtifact(
                    "reasoning-promotion",
                    ArtifactType.REASONING_OUTPUT,
                    source_evidence_ids={"e-synthetic"},
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_reasoning",
                ),
                ExpectedBehaviorType.REASONING_NOT_CLAIM_MUTATION,
                {"synthetic", "reality-boundary", "reasoning"},
                target=ArtifactType.CLAIM,
            ),
            self._boundary_scenario(
                "synthetic-eval-to-evidence",
                "Synthetic Evaluation To Evidence Attempt",
                CognitiveArtifact(
                    "eval-promotion",
                    ArtifactType.SYNTHETIC_EVALUATION,
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_evaluation",
                ),
                ExpectedBehaviorType.SYNTHETIC_NOT_REAL_EVIDENCE,
                {"synthetic", "reality-boundary", "evaluation"},
            ),
            self._boundary_scenario(
                "synthetic-speculation-promotion",
                "Speculative Hypothesis Promotion Attempt",
                CognitiveArtifact(
                    "speculation-promotion",
                    ArtifactType.SPECULATIVE_HYPOTHESIS,
                    source_evidence_ids={"e-synthetic"},
                    provenance_ids={"prov-synthetic"},
                    layer_origin="synthetic_reasoning",
                ),
                ExpectedBehaviorType.SPECULATION_REMAINS_SPECULATION,
                {"synthetic", "reality-boundary", "speculation"},
            ),
        ]

    def attention_scenarios(self) -> list[EvaluationScenario]:
        gate = AttentionGate()
        contamination = AttentionCandidate(
            "attention-contamination",
            "evidence",
            provenance_ids={"prov"},
            contamination_risk=0.9,
            novelty=0.7,
        )
        contradiction = AttentionCandidate(
            "attention-contradiction",
            "claim",
            provenance_ids={"prov"},
            contradiction_pressure=0.9,
            contested=True,
        )
        repeated_a = AttentionCandidate(
            "attention-lineage-a",
            "evidence",
            provenance_ids={"prov-a"},
            lineage_id="same",
            recurrence=0.9,
        )
        repeated_b = AttentionCandidate(
            "attention-lineage-b",
            "evidence",
            provenance_ids={"prov-b"},
            lineage_id="same",
            recurrence=0.9,
        )
        fragile = AttentionCandidate("attention-fragile", "evidence", provenance_ids=set())
        archived = AttentionCandidate(
            "attention-archived",
            "memory",
            provenance_ids={"prov"},
            archived=True,
            novelty=0.8,
        )
        focus_warning = AttentionCandidate(
            "attention-focus-warning",
            "evidence",
            text="radar focus match",
            provenance_ids=set(),
            entity_ids={"entity-focus"},
        )
        duplicate = AttentionCandidate(
            "attention-low-novelty",
            "evidence",
            provenance_ids={"prov"},
            lineage_id="same",
            novelty=0.1,
        )
        return [
            self._attention_scenario(
                "synthetic-attention-contamination",
                "High-Salience Contamination",
                gate.apply([contamination], limit=1),
                [ExpectedBehaviorType.ATTENTION_CONTAMINATION_WARNING_VISIBLE],
                {"synthetic", "attention", "contamination"},
            ),
            self._attention_scenario(
                "synthetic-attention-contradiction",
                "Contradiction-Priority Attention",
                gate.apply([contradiction], policy="contradiction_first", limit=1),
                [ExpectedBehaviorType.ATTENTION_CONTRADICTION_VISIBLE],
                {"synthetic", "attention", "contradiction"},
            ),
            self._attention_scenario(
                "synthetic-attention-lineage-suppression",
                "Repeated Same-Lineage Attention Suppression",
                gate.apply([repeated_a, repeated_b, duplicate], limit=2),
                [ExpectedBehaviorType.ATTENTION_SAME_LINEAGE_SUPPRESSED],
                {"synthetic", "attention", "lineage"},
            ),
            self._attention_scenario(
                "synthetic-attention-fragile-provenance",
                "Fragile Provenance Escalation",
                gate.apply([fragile], policy="provenance_first", limit=1),
                [ExpectedBehaviorType.ATTENTION_PROVENANCE_WARNING_VISIBLE],
                {"synthetic", "attention", "provenance"},
            ),
            self._attention_scenario(
                "synthetic-attention-archived-reactivation",
                "Archived Memory Reactivation Candidate",
                gate.apply([archived], policy="exploratory", limit=1),
                [ExpectedBehaviorType.ATTENTION_SALIENCE_NOT_CONFIDENCE],
                {"synthetic", "attention", "archived"},
            ),
            self._attention_scenario(
                "synthetic-attention-focus-provenance",
                "Focus Match With Provenance Warning",
                gate.apply([focus_warning], limit=1),
                [ExpectedBehaviorType.ATTENTION_PROVENANCE_WARNING_VISIBLE],
                {"synthetic", "attention", "focus"},
            ),
            self._attention_scenario(
                "synthetic-attention-low-novelty-deferral",
                "Low-Novelty Duplicate Deferral",
                gate.apply([repeated_a, repeated_b, duplicate], limit=1),
                [ExpectedBehaviorType.ATTENTION_SAME_LINEAGE_SUPPRESSED],
                {"synthetic", "attention", "deferral"},
            ),
        ]

    def claim_normalization_scenarios(self) -> list[EvaluationScenario]:
        normalized = NormalizedClaim(
            normalized_claim_id="synthetic-normalized-claim",
            canonical_key=ClaimCanonicalKey("bright-light", "reported", ("bright", "light")),
            canonical_text="Witness reported bright light",
            candidate_claim_ids={"candidate-1", "candidate-2"},
            origin_types={CandidateClaimOrigin.FROM_REPORTED_CLAIM},
            evidence_ids={"e1", "e2"},
            provenance_ids={"p1", "p2"},
            lineage_ids={"same"},
            unsupported=True,
            confidence=0.0,
            notes=["synthetic claim normalization scenario"],
        )
        return [
            self._scenario(
                "synthetic-claim-normalization-no-validation",
                "Claim Normalization Is Not Validation",
                EvaluationInput(normalized_claims=[normalized]),
                [
                    ExpectedBehaviorType.CLAIM_NORMALIZATION_NOT_VALIDATION,
                    ExpectedBehaviorType.NORMALIZED_CLAIMS_UNSUPPORTED,
                ],
                {"synthetic", "claim-normalization"},
            )
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

    def _boundary_scenario(
        self,
        scenario_id: str,
        title: str,
        artifact: CognitiveArtifact,
        behavior: ExpectedBehaviorType,
        tags: set[str],
        *,
        target: ArtifactType = ArtifactType.EVIDENCE,
    ) -> EvaluationScenario:
        engine = RealityBoundaryEngine()
        engine.register_artifact(artifact)
        if target is ArtifactType.CLAIM:
            engine.prevent_claim_mutation(artifact.artifact_id)
        elif behavior is ExpectedBehaviorType.SEMANTIC_CLUSTER_NOT_GRAPH_SUPPORT:
            engine.prevent_graph_support(artifact.artifact_id)
        else:
            engine.prevent_evidence_promotion(artifact.artifact_id)
        return self._scenario(
            scenario_id,
            title,
            EvaluationInput(cognitive_state=engine.registry.state),
            [behavior],
            tags,
        )

    def _attention_scenario(
        self,
        scenario_id: str,
        title: str,
        decision: AttentionDecision,
        behaviors: list[ExpectedBehaviorType],
        tags: set[str],
    ) -> EvaluationScenario:
        return self._scenario(
            scenario_id,
            title,
            EvaluationInput(attention_decision=decision, before_state_hash="attention", after_state_hash="attention"),
            behaviors,
            tags,
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
