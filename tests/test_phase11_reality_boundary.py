from roswell_uap_cortex import (
    ArtifactType,
    ClaimMatrixStatus,
    ClaimNode,
    CognitiveArtifact,
    CognitiveArtifactRegistry,
    EvaluationHarness,
    ExpectedBehaviorType,
    RealityBoundaryEngine,
    RecursiveInferenceGuard,
    RelationshipGraphEngine,
    ScenarioFactory,
)


def artifact(
    artifact_id: str,
    artifact_type: ArtifactType,
    *,
    sources: set[str] | None = None,
    evidence_ids: set[str] | None = None,
    provenance: set[str] | None = None,
) -> CognitiveArtifact:
    return CognitiveArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        content=f"synthetic {artifact_type.value}",
        source_artifact_ids=sources or set(),
        source_evidence_ids=evidence_ids or set(),
        provenance_ids=provenance if provenance is not None else {"prov-synthetic"},
        layer_origin="synthetic_test",
    )


def test_discourse_cannot_become_evidence_automatically() -> None:
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("d1", ArtifactType.DISCOURSE_OUTPUT))

    violation = engine.prevent_evidence_promotion("d1")

    assert violation is not None
    assert violation.violation_type == "discourse_not_evidence"


def test_reasoning_outputs_cannot_mutate_claims() -> None:
    claim = ClaimNode(text="unsupported", canonical_topic="x", status=ClaimMatrixStatus.UNSUPPORTED)
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("r1", ArtifactType.REASONING_OUTPUT))

    violation = engine.prevent_claim_mutation("r1")

    assert violation is not None
    assert violation.violation_type == "reasoning_not_claim_mutation"
    assert claim.status is ClaimMatrixStatus.UNSUPPORTED


def test_semantic_clusters_cannot_create_graph_support() -> None:
    graph = RelationshipGraphEngine()
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("cluster-1", ArtifactType.SEMANTIC_CLUSTER))

    violation = engine.prevent_graph_support("cluster-1")

    assert violation is not None
    assert violation.violation_type == "semantic_cluster_not_graph_support"
    assert graph.edges == {}


def test_recursive_reasoning_loops_are_detected() -> None:
    registry = CognitiveArtifactRegistry()
    registry.register(artifact("r1", ArtifactType.REASONING_OUTPUT))
    registry.register(artifact("r2", ArtifactType.REASONING_OUTPUT, sources={"r1"}))

    warnings = registry.contamination_chain("r2")

    assert any(warning.warning_type == "reasoning_about_reasoning" for warning in warnings)


def test_self_citation_loops_emit_warnings() -> None:
    registry = CognitiveArtifactRegistry()
    registry.register(artifact("self", ArtifactType.DISCOURSE_OUTPUT, sources={"self"}))

    assert any(warning.warning_type == "self_citation_loop" for warning in registry.state.warnings)


def test_recursion_depth_remains_bounded() -> None:
    registry = CognitiveArtifactRegistry(recursive_guard=RecursiveInferenceGuard(max_depth=1))
    registry.safety_guard.max_recursion_depth = 1
    registry.register(artifact("a", ArtifactType.EXTERNAL_INPUT))
    registry.register(artifact("b", ArtifactType.REASONING_OUTPUT, sources={"a"}))
    registry.register(artifact("c", ArtifactType.DISCOURSE_OUTPUT, sources={"b"}))

    assert any(violation.violation_type == "recursion_depth_exceeded" for violation in registry.state.violations)


def test_artifact_provenance_chains_are_preserved() -> None:
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("e1", ArtifactType.EXTERNAL_INPUT, evidence_ids={"e1"}))
    engine.register_artifact(artifact("r1", ArtifactType.REASONING_OUTPUT, sources={"e1"}))
    engine.register_artifact(artifact("d1", ArtifactType.DISCOURSE_OUTPUT, sources={"r1"}))

    chain = engine.provenance_chain("d1")

    assert [record.artifact_id for record in chain] == ["d1", "r1", "e1"]
    assert chain[0].provenance_ids == {"prov-synthetic"}


def test_invalid_artifact_promotion_is_blocked() -> None:
    registry = CognitiveArtifactRegistry()
    registry.register(artifact("retrieval-1", ArtifactType.RETRIEVAL_RESULT))

    violation = registry.validate_promotion("retrieval-1", ArtifactType.EVIDENCE)

    assert violation is not None
    assert violation.violation_type == "automatic_promotion_blocked"


def test_synthetic_evaluation_artifacts_remain_synthetic() -> None:
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("eval-1", ArtifactType.SYNTHETIC_EVALUATION))

    violation = engine.prevent_evidence_promotion("eval-1")

    assert violation is not None
    assert violation.violation_type == "synthetic_not_real_evidence"


def test_speculative_hypotheses_remain_speculative() -> None:
    engine = RealityBoundaryEngine()
    engine.register_artifact(artifact("hyp-1", ArtifactType.SPECULATIVE_HYPOTHESIS))

    violation = engine.prevent_evidence_promotion("hyp-1")

    assert violation is not None
    assert violation.violation_type == "speculation_remains_speculation"


def test_missing_provenance_blocks_unsafe_promotion() -> None:
    registry = CognitiveArtifactRegistry()
    registry.register(artifact("external-1", ArtifactType.EXTERNAL_INPUT, provenance=set()))

    violation = registry.validate_promotion("external-1", ArtifactType.EVIDENCE, explicit=True)

    assert violation is not None
    assert violation.violation_type == "missing_provenance_blocks_promotion"


def test_reality_boundary_checks_are_deterministic() -> None:
    def run_once() -> list[tuple[str, str]]:
        engine = RealityBoundaryEngine()
        engine.register_artifact(artifact("d1", ArtifactType.DISCOURSE_OUTPUT, sources={"d1"}))
        engine.validate_cognitive_separation()
        return [
            (violation.violation_type, ",".join(sorted(violation.artifact_ids)))
            for violation in engine.registry.state.violations
        ]

    assert run_once() == run_once()


def test_reality_boundary_evaluation_scenarios_are_registered() -> None:
    scenarios = [
        scenario
        for scenario in ScenarioFactory().all()
        if "reality-boundary" in scenario.tags
    ]
    report = EvaluationHarness().run(scenarios)

    assert scenarios
    assert report.overall_pass_rate == 1.0
    assert any(
        ExpectedBehaviorType.RECURSIVE_INFERENCE_DETECTED in result.behavior_results
        for result in report.results
    )
