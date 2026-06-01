from roswell_uap_cortex import (
    ActivatedContext,
    ClaimMatrixEngine,
    ClaimNode,
    ClaimReviewDocket,
    ClaimReviewItem,
    CognitiveReasoningEngine,
    DiscourseEngine,
    DiscourseRequest,
    EvidenceItem,
    GraphNode,
    GraphNodeType,
    ProvenanceRecord,
    ReasoningRequest,
    RelationshipGraphEngine,
    ReviewBundleBuilder,
    ReviewContextAdapter,
    ReviewDecisionType,
    ReviewInfluencePolicy,
    ReviewInfluenceWarningType,
    ReviewPriority,
    ReviewSessionEngine,
    SourceReviewDocket,
    SourceReviewItem,
    SourceReviewPriority,
    SourceRiskSignal,
    UncertaintyNote,
    WorkingMemoryEngine,
)


def claim_docket() -> ClaimReviewDocket:
    item = ClaimReviewItem(
        normalized_claim_id="claim-1",
        canonical_topic="bright-light",
        canonical_text="observer saw a bright light",
        priority=ReviewPriority.HIGH,
        priority_score=0.8,
        contradiction_summaries=[],
        provenance_ids=set(),
        unsupported=True,
        confidence=0.0,
    )
    return ClaimReviewDocket("claim-docket", "Claim Docket", items=[item])


def source_docket() -> SourceReviewDocket:
    item = SourceReviewItem(
        source_id="source-1",
        priority=SourceReviewPriority.HIGH,
        priority_score=0.7,
        risk_score=0.7,
        evidence_ids={"evidence-1"},
    )
    item.risk_signals.append(SourceRiskSignal("missing_provenance", 0.7, "missing provenance"))
    return SourceReviewDocket("source-docket", "Source Docket", items=[item])


def review_session():
    state = WorkingMemoryEngine().build_state(
        query="bright light",
        claim_dockets=[claim_docket()],
        source_dockets=[source_docket()],
    )
    session = ReviewSessionEngine().start_session("Boundary Review", state)
    ReviewSessionEngine().record_decision(
        session,
        item_id="claim-1",
        item_type="claim_review_item",
        decision_type=ReviewDecisionType.REVIEWED,
        notes=["human read the docket"],
    )
    ReviewSessionEngine().record_decision(
        session,
        item_id="source-1",
        item_type="source_review_item",
        decision_type=ReviewDecisionType.REQUEST_MORE_PROVENANCE,
        notes=["needs original source URI"],
    )
    return session


def test_review_influence_policy_allows_attention_context_and_discourse_only() -> None:
    influence = ReviewInfluencePolicy().evaluate(
        review_session(),
        claim_dockets=[claim_docket()],
        source_dockets=[source_docket()],
    )

    assert "claim-1" in influence.prioritized_ids
    assert "claim-1" in influence.unresolved_ids
    assert "source-1" in influence.deferred_ids
    assert "source-1" in influence.provenance_gap_ids
    assert "source-1" in influence.source_review_warning_ids
    assert {
        ReviewInfluenceWarningType.REVIEW_STATE_NOT_TRUTH,
        ReviewInfluenceWarningType.REVIEWED_NOT_CONFIRMED,
        ReviewInfluenceWarningType.DEFERRED_NOT_ERASED,
        ReviewInfluenceWarningType.SOURCE_RISK_NOT_REJECTION,
        ReviewInfluenceWarningType.PRIORITY_NOT_CONFIDENCE,
        ReviewInfluenceWarningType.PROVENANCE_GAP_VISIBLE,
    }.issubset({warning.warning_type for warning in influence.warnings})


def test_reviewed_claim_does_not_gain_claim_matrix_confidence() -> None:
    claim = ClaimNode(id="claim-1", text="observer saw a bright light", canonical_topic="bright-light")
    matrix = ClaimMatrixEngine()
    entry = matrix.register_unsupported_candidate_topic("bright-light", claim)
    before = (entry.status, entry.claim_confidence, claim.status, claim.confidence)

    ReviewInfluencePolicy().evaluate(review_session(), claim_dockets=[claim_docket()])

    after = (entry.status, entry.claim_confidence, claim.status, claim.confidence)
    assert after == before


def test_review_context_adapter_preserves_deferred_and_unresolved_visibility() -> None:
    influence = ReviewInfluencePolicy().evaluate(
        review_session(),
        claim_dockets=[claim_docket()],
        source_dockets=[source_docket()],
    )
    activated = ReviewContextAdapter().adapt(ActivatedContext(), influence)

    notes = "\n".join(activated.uncertainty_notes)
    assert "deferred review items remain unresolved" in notes
    assert "claim claim-1 remains unsupported" in notes
    assert "source source-1 has review warnings" in notes


def test_review_influence_can_prioritize_reasoning_context_without_confirming_claims() -> None:
    influence = ReviewInfluencePolicy().evaluate(review_session(), claim_dockets=[claim_docket()])
    claim = ClaimNode(id="claim-1", text="observer saw a bright light", canonical_topic="bright-light")
    output = CognitiveReasoningEngine().reason(
        ReasoningRequest(query="bright light", activated_context=ActivatedContext(), max_context_items=4),
        claims_by_id={"claim-1": claim},
        review_influence=influence,
    )

    assert "claim-1" in output.supporting_context_ids
    assert claim.confidence == 0.0
    assert any("review workflow state may guide attention" in note.note for note in output.uncertainty_notes)
    assert any("Unsupported claim remains unsupported" in note.note for note in output.uncertainty_notes)


def test_session_decisions_do_not_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(id="claim-1", node_type=GraphNodeType.CLAIM, label="claim"))

    ReviewInfluencePolicy().evaluate(review_session(), claim_dockets=[claim_docket()])

    assert graph.edges == {}


def test_review_bundle_does_not_affect_claim_matrix_confidence() -> None:
    claim = ClaimNode(id="claim-1", text="observer saw a bright light", canonical_topic="bright-light")
    matrix = ClaimMatrixEngine()
    entry = matrix.register_unsupported_candidate_topic("bright-light", claim)
    session = review_session()

    ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()])

    assert entry.claim_confidence == 0.0
    assert claim.confidence == 0.0


def test_source_review_risk_flag_does_not_reject_source() -> None:
    influence = ReviewInfluencePolicy().evaluate(review_session(), source_dockets=[source_docket()])

    assert "source-1" in influence.source_review_warning_ids
    assert any(
        warning.warning_type is ReviewInfluenceWarningType.SOURCE_RISK_NOT_REJECTION
        for warning in influence.warnings
    )
    assert not any("rejected" in note.casefold() for note in influence.uncertainty_notes)


def test_discourse_can_mention_review_state_without_mutating_evidence() -> None:
    evidence = EvidenceItem(
        id="evidence-1",
        summary="Synthetic evidence summary",
        source_id="source-1",
        evidence_type="note",
    )
    provenance = ProvenanceRecord(
        evidence_id="evidence-1",
        source_uri="fixture://evidence-1",
        source_kind="note",
        ingestion_method="fixture",
        extraction_method="fixture",
        original_input_id="raw-1",
    )
    influence = ReviewInfluencePolicy().evaluate(review_session(), source_dockets=[source_docket()])
    before = evidence.summary
    reasoning = CognitiveReasoningEngine().reason(
        ReasoningRequest(
            query="bright light",
            activated_context=ReviewContextAdapter().adapt(
                ActivatedContext(activated_evidence_ids={"evidence-1"}),
                influence,
            ),
            max_context_items=4,
        ),
        evidence_by_id={"evidence-1": evidence},
        provenance_by_evidence_id={"evidence-1": provenance},
        review_influence=influence,
    )
    discourse = DiscourseEngine().build(
        DiscourseRequest("bright light", ActivatedContext(activated_evidence_ids={"evidence-1"}), reasoning),
        evidence_by_id={"evidence-1": evidence},
        provenance_by_evidence_id={"evidence-1": provenance},
    )

    assert evidence.summary == before
    assert any("review workflow state may guide attention" in item for item in discourse.uncertainty_summary.items)
    assert discourse.citations


def test_audit_and_bundle_warnings_do_not_enter_review_influence_as_evidence() -> None:
    influence = ReviewInfluencePolicy().evaluate(review_session())

    assert all(warning.warning_type is not ReviewInfluenceWarningType.AUDIT_NOT_EVIDENCE for warning in influence.warnings)
    assert all(warning.warning_type is not ReviewInfluenceWarningType.BUNDLE_NOT_REASONING_INPUT for warning in influence.warnings)
    assert not any(signal.item_type == "evidence" for signal in influence.signals)
