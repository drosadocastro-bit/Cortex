from roswell_uap_cortex import (
    ActivatedContext,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    AttentionCandidate,
    AttentionEngine,
    AttentionFocusBuilder,
    AttentionGate,
    AttentionSignal,
    AttentionWarningType,
    ClaimNode,
    ContextWindowBuilder,
    EvaluationHarness,
    ExpectedBehaviorType,
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    SaliencePolicyEngine,
    ScenarioFactory,
)


def candidate(
    record_id: str,
    *,
    lineage_id: str | None = None,
    provenance: bool = True,
    contradiction: float = 0.0,
    contamination: float = 0.0,
    novelty: float = 0.5,
    archived: bool = False,
    contested: bool = False,
    text: str = "radar sighting",
) -> AttentionCandidate:
    return AttentionCandidate(
        record_id=record_id,
        record_type="evidence",
        label=record_id,
        text=text,
        tags={"radar"},
        entity_ids={"entity-1"},
        provenance_ids={f"prov-{record_id}"} if provenance else set(),
        lineage_id=lineage_id,
        contradiction_pressure=contradiction,
        contamination_risk=contamination,
        novelty=novelty,
        archived=archived,
        contested=contested,
    )


def test_salience_scores_are_bounded_between_zero_and_one() -> None:
    score = AttentionEngine().score(candidate("a", contradiction=5.0, contamination=5.0))

    assert 0.0 <= score.final_salience_score <= 1.0
    assert score.bounded


def test_high_contradiction_pressure_increases_salience() -> None:
    engine = AttentionEngine()
    low = engine.score(candidate("low", contradiction=0.0)).final_salience_score
    high = engine.score(candidate("high", contradiction=0.9)).final_salience_score

    assert high > low


def test_fragile_missing_provenance_increases_review_priority_but_not_confidence() -> None:
    decision = AttentionGate().apply([candidate("fragile", provenance=False)], policy="provenance_first")

    assert decision.selected_for_review[0].record_id == "fragile"
    assert decision.selected_for_review[0].metadata.get("confidence") is None
    assert any("missing_provenance_review" in score.reason_codes for score in decision.salience_by_id.values())


def test_contamination_risk_creates_warnings() -> None:
    decision = AttentionGate().apply([candidate("dirty", contamination=0.9)])

    assert AttentionWarningType.CONTAMINATION_SALIENT_NOT_TRUSTED in {
        warning.warning_type for warning in decision.attention_warnings
    }


def test_same_lineage_duplicates_are_suppressed_or_downgraded() -> None:
    decision = AttentionGate().apply(
        [
            candidate("a", lineage_id="same", novelty=0.8),
            candidate("b", lineage_id="same", novelty=0.8),
        ],
        limit=2,
    )

    assert "same_lineage_downgraded" in decision.salience_by_id["b"].reason_codes
    assert decision.salience_by_id["b"].final_salience_score < decision.salience_by_id["a"].final_salience_score


def test_contested_items_are_preserved_in_attention_output() -> None:
    decision = AttentionGate().apply(
        [candidate("plain"), candidate("contested", contested=True, contradiction=0.8)],
        limit=1,
    )

    assert "contested" in {item.record_id for item in decision.selected_for_review}


def test_archived_memories_are_not_deleted() -> None:
    archived = candidate("archived", archived=True, novelty=0.2)
    decision = AttentionGate().apply([archived], limit=0)

    assert decision.archived_records_considered == [archived]
    assert decision.deferred_records == [archived]


def test_focus_matching_increases_salience_without_overriding_guardrails() -> None:
    focus = AttentionFocusBuilder().build("radar", target_entities={"entity-1"})
    engine = AttentionEngine()
    focused = engine.score(candidate("focus", provenance=False), focus).final_salience_score
    unrelated_candidate = candidate("other", text="unrelated text", provenance=False)
    unrelated_candidate.entity_ids = set()
    unrelated = engine.score(unrelated_candidate, focus).final_salience_score

    assert focused > unrelated
    assert AttentionWarningType.PROVENANCE_WARNING_VISIBLE in {
        warning.warning_type for warning in engine.score(candidate("focus", provenance=False), focus).warnings
    }


def test_conservative_and_exploratory_policies_produce_deterministic_different_rankings() -> None:
    records = [
        candidate("novel", novelty=1.0, text="radar anomaly"),
        candidate("fragile", provenance=False, novelty=0.1, text="old note"),
    ]
    focus = AttentionFocusBuilder().build("radar")
    gate = AttentionGate()
    conservative = [item.record_id for item in gate.apply(records, focus, policy="provenance_first").selected_records]
    exploratory = [item.record_id for item in gate.apply(records, focus, policy="exploratory").selected_records]

    assert conservative != exploratory
    assert gate.apply(records, focus, policy="exploratory").selected_records[0].record_id == exploratory[0]


def test_policy_presets_never_disable_required_guardrails() -> None:
    policies = SaliencePolicyEngine().all_policies().values()

    assert all(policy.preserve_contradictions for policy in policies)
    assert all(policy.preserve_provenance_warnings for policy in policies)
    assert all(policy.preserve_association_not_confirmation for policy in policies)
    assert all(policy.preserve_reality_boundaries for policy in policies)


def test_attention_gate_defers_rather_than_deletes_low_priority_records() -> None:
    records = [candidate("a"), candidate("b"), candidate("c")]
    decision = AttentionGate().apply(records, limit=1)

    assert len(decision.selected_records) == 1
    assert {item.record_id for item in decision.deferred_records} == {"a", "b", "c"} - {
        decision.selected_records[0].record_id
    }


def test_attention_does_not_create_graph_edges_claims_evidence_or_confirmations() -> None:
    graph = RelationshipGraphEngine()
    claim = ClaimNode(text="unsupported", canonical_topic="x")
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))

    AttentionGate().apply([candidate("a", contradiction=0.7)])

    assert graph.edges == {}
    assert claim.confidence == 0.0
    assert claim.evidence_ids == set()


def test_attention_integration_preserves_context_builder_backwards_compatibility() -> None:
    activated = ActivatedContext()
    candidates = [
        AssociationCandidate(
            record_id="a",
            record_type="evidence",
            label="a",
            score=AssociationScore(final_association_score=0.2),
            association_label=AssociationLabel.POSSIBLE_ASSOCIATION,
        ),
        AssociationCandidate(
            record_id="b",
            record_type="evidence",
            label="b",
            score=AssociationScore(final_association_score=0.1),
            association_label=AssociationLabel.POSSIBLE_ASSOCIATION,
        ),
    ]
    plain = ContextWindowBuilder(max_items=2).build(activated, candidates=candidates)
    attention = AttentionGate().apply([candidate("b", novelty=1.0), candidate("a", novelty=0.1)])
    guided = ContextWindowBuilder(max_items=2).build(
        activated,
        candidates=candidates,
        attention_decision=attention,
    )

    assert [item.record_id for item in plain.selected_candidates] == ["a", "b"]
    assert [item.record_id for item in guided.selected_candidates] == ["b", "a"]


def test_synthetic_attention_evaluation_scenarios_remain_deterministic() -> None:
    scenarios = [scenario for scenario in ScenarioFactory().all() if "attention" in scenario.tags]
    report = EvaluationHarness().run(scenarios)

    assert scenarios
    assert report.overall_pass_rate == 1.0
    assert any(
        ExpectedBehaviorType.ATTENTION_SAME_LINEAGE_SUPPRESSED in result.behavior_results
        for result in report.results
    )


def test_salience_score_is_review_priority_not_truth_confidence_component() -> None:
    score = AttentionEngine().score(candidate("a", contamination=0.9))

    assert AttentionSignal.SOURCE_TRUST in score.component_scores
    assert "confidence" not in {reason.casefold() for reason in score.reason_codes}
