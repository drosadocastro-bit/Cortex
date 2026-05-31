from roswell_uap_cortex import (
    ActivatedContext,
    ClaimMatrixStatus,
    ClaimReviewDocket,
    ClaimReviewItem,
    DiscourseResponse,
    DiscourseSection,
    EvidenceAssessmentSummary,
    GraphNode,
    GraphNodeType,
    ReasoningOutput,
    RelationshipGraphEngine,
    ReviewDecisionType,
    ReviewPriority,
    ReviewSessionEngine,
    SessionFormatter,
    SourceReviewDocket,
    SourceReviewItem,
    SourceReviewPriority,
    SourceRiskSignal,
    UncertaintyNote,
    WorkingMemoryEngine,
)


def claim_docket() -> ClaimReviewDocket:
    support = EvidenceAssessmentSummary("e-support", "possible_support", support_score=0.7)
    contradiction = EvidenceAssessmentSummary("e-contradiction", "possible_contradiction", contradiction_score=0.8)
    uncertainty = EvidenceAssessmentSummary("e-uncertain", "uncertain", uncertainty_score=0.5)
    item = ClaimReviewItem(
        normalized_claim_id="claim-1",
        canonical_topic="bright-light",
        canonical_text="observer saw bright light",
        priority=ReviewPriority.HIGH,
        priority_score=0.7,
        support_summaries=[support],
        contradiction_summaries=[contradiction],
        uncertainty_summaries=[uncertainty],
        unsupported=True,
        confidence=0.0,
    )
    return ClaimReviewDocket("claim-docket", "Claim Docket", items=[item])


def source_docket() -> SourceReviewDocket:
    item = SourceReviewItem(
        source_id="fixture://source",
        priority=SourceReviewPriority.MEDIUM,
        priority_score=0.4,
        risk_score=0.4,
        evidence_ids={"e-source"},
        notes=["risk visible"],
    )
    item.risk_signals.append(SourceRiskSignal("missing_provenance", 0.4, "missing provenance"))
    return SourceReviewDocket("source-docket", "Source Docket", items=[item])


def empty_discourse() -> DiscourseResponse:
    empty = DiscourseSection("empty")
    return DiscourseResponse(
        observed_evidence=empty,
        possible_associations=empty,
        contradictions=DiscourseSection("Contradictions", items=["claim-1 conflicts with evidence"]),
        weak_associations=empty,
        speculative_hypotheses=empty,
        provenance_notes=empty,
        uncertainty_summary=DiscourseSection("Uncertainty", items=["uncertainty remains visible"]),
        missing_information=empty,
    )


def test_session_starts_deterministically() -> None:
    state = WorkingMemoryEngine().build_state(query="lights", claim_dockets=[claim_docket()])
    first = ReviewSessionEngine().start_session("Review", state)
    second = ReviewSessionEngine().start_session("Review", state)

    assert first.session_id == second.session_id
    assert first.created_at == second.created_at


def test_claim_and_source_dockets_enter_working_memory() -> None:
    state = WorkingMemoryEngine().build_state(
        query="lights",
        claim_dockets=[claim_docket()],
        source_dockets=[source_docket()],
    )

    assert state.active_claim_docket_ids == {"claim-docket"}
    assert state.active_source_docket_ids == {"source-docket"}
    assert "claim-1" in state.active_focus.focus_ids
    assert "fixture://source" in state.active_focus.source_ids


def test_reviewed_items_are_tracked_without_mutating_original_records() -> None:
    docket = claim_docket()
    before_status = ClaimMatrixStatus.UNSUPPORTED
    session = ReviewSessionEngine().start_session("Review", WorkingMemoryEngine().build_state(claim_dockets=[docket]))

    delta = ReviewSessionEngine().record_decision(
        session,
        item_id="claim-1",
        item_type="claim_review_item",
        decision_type=ReviewDecisionType.REVIEWED,
        notes=["looked at only"],
    )

    assert delta.added_reviewed_ids == {"claim-1"}
    assert session.state.reviewed_items[0].item_id == "claim-1"
    assert docket.items[0].unsupported
    assert before_status is ClaimMatrixStatus.UNSUPPORTED


def test_deferred_items_remain_visible_and_unresolved() -> None:
    session = ReviewSessionEngine().start_session("Review")

    delta = ReviewSessionEngine().record_decision(
        session,
        item_id="source-1",
        item_type="source_review_item",
        decision_type=ReviewDecisionType.DEFERRED,
        notes=["needs source provenance"],
    )

    assert delta.added_deferred_ids == {"source-1"}
    assert "source-1" in session.state.unresolved_item_ids
    assert session.state.deferred_items[0].reason == "needs source provenance"


def test_unresolved_contradictions_remain_visible() -> None:
    state = WorkingMemoryEngine().build_state(claim_dockets=[claim_docket()])

    assert "claim-1" in state.contradiction_ids
    assert "claim-1" in state.unresolved_item_ids


def test_uncertainty_notes_are_preserved_from_context_reasoning_and_discourse() -> None:
    context = ActivatedContext(uncertainty_notes=["activated uncertainty"])
    reasoning = ReasoningOutput(
        contested_context_ids={"context-1"},
        uncertainty_notes=[UncertaintyNote("reasoning uncertainty")],
    )
    state = WorkingMemoryEngine().build_state(
        activated_context=context,
        reasoning_output=reasoning,
        discourse_response=empty_discourse(),
    )

    assert "activated uncertainty" in state.uncertainty_notes
    assert "reasoning uncertainty" in state.uncertainty_notes
    assert "uncertainty remains visible" in state.uncertainty_notes
    assert "context-1" in state.unresolved_item_ids


def test_session_deltas_are_deterministic() -> None:
    first = ReviewSessionEngine().start_session("Review")
    second = ReviewSessionEngine().start_session("Review")

    delta_a = ReviewSessionEngine().record_decision(
        first,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.KEEP_UNRESOLVED,
    )
    delta_b = ReviewSessionEngine().record_decision(
        second,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.KEEP_UNRESOLVED,
    )

    assert delta_a == delta_b


def test_resume_preserves_prior_state() -> None:
    session = ReviewSessionEngine().start_session("Review")
    ReviewSessionEngine().record_decision(
        session,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.REVIEWED,
    )

    resumed = ReviewSessionEngine().resume_session(session)

    assert resumed.state.reviewed_items[0].item_id == "claim-1"
    assert "session resumed without mutating reviewed records" in resumed.notes


def test_review_decisions_do_not_confirm_claims_or_reject_sources() -> None:
    session = ReviewSessionEngine().start_session("Review")
    ReviewSessionEngine().record_decision(
        session,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.REVIEWED,
    )
    ReviewSessionEngine().record_decision(
        session,
        item_id="fixture://source",
        item_type="source",
        decision_type=ReviewDecisionType.REQUEST_SOURCE_REVIEW,
    )

    assert all("confirm" not in " ".join(decision.notes).casefold() for decision in session.decisions)
    assert "fixture://source" in session.state.unresolved_item_ids


def test_formatter_avoids_certainty_inflation() -> None:
    state = WorkingMemoryEngine().build_state(claim_dockets=[claim_docket()], source_dockets=[source_docket()])
    session = ReviewSessionEngine().start_session("Review", state)
    text = SessionFormatter().format(session)

    assert "not claim confirmation, source rejection, or evidence mutation" in text
    assert "Unresolved items" in text


def test_no_graph_edges_or_evidence_mutation() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    docket = claim_docket()
    before = docket.items[0].canonical_text

    WorkingMemoryEngine().build_state(claim_dockets=[docket])

    assert graph.edges == {}
    assert docket.items[0].canonical_text == before
