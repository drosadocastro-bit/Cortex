from roswell_uap_cortex import (
    ClaimReviewDocket,
    ClaimReviewItem,
    DiscourseCitation,
    EvidenceAssessmentSummary,
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    ReviewBundleBuilder,
    ReviewBundleFormatter,
    ReviewBundleGuardrails,
    ReviewBundleSection,
    ReviewDecisionType,
    ReviewPriority,
    ReviewSessionEngine,
    SessionAuditLogger,
    SourceReviewDocket,
    SourceReviewItem,
    SourceReviewPriority,
    WorkingMemoryEngine,
)


def claim_docket(with_citation: bool = True) -> ClaimReviewDocket:
    item = ClaimReviewItem(
        normalized_claim_id="claim-1",
        canonical_topic="bright-light",
        canonical_text="observer saw bright light",
        priority=ReviewPriority.HIGH,
        priority_score=0.7,
        support_summaries=[EvidenceAssessmentSummary("e1", "possible_support", support_score=0.6)],
        contradiction_summaries=[EvidenceAssessmentSummary("e2", "possible_contradiction", contradiction_score=0.8)],
        uncertainty_summaries=[EvidenceAssessmentSummary("e3", "uncertain", uncertainty_score=0.4)],
    )
    citations = [DiscourseCitation(evidence_id="e1", provenance_id="p1", label="evidence:e1 | provenance:p1")] if with_citation else []
    return ClaimReviewDocket("claim-docket", "Claim Docket", items=[item], citations=citations)


def source_docket(with_citation: bool = True) -> SourceReviewDocket:
    item = SourceReviewItem(
        source_id="fixture://source",
        priority=SourceReviewPriority.MEDIUM,
        priority_score=0.4,
        risk_score=0.4,
        reliability_score=0.5,
        evidence_ids={"e1"},
    )
    citations = [DiscourseCitation(evidence_id="e1", source_id="fixture://source", provenance_id="p1", label="source citation")] if with_citation else []
    return SourceReviewDocket("source-docket", "Source Docket", items=[item], citations=citations)


def session_and_trail():
    state = WorkingMemoryEngine().build_state(
        query="review bundle",
        claim_dockets=[claim_docket()],
        source_dockets=[source_docket()],
    )
    engine = ReviewSessionEngine()
    session = engine.start_session("Bundle Session", state)
    engine.record_decision(
        session,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.DEFERRED,
        notes=["needs provenance"],
    )
    logger = SessionAuditLogger()
    trail = logger.build_trail(session, [logger.start(session), logger.decision(session, session.decisions[-1])])
    return session, trail


def test_bundle_builds_deterministically() -> None:
    session, trail = session_and_trail()
    first = ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()], audit_trail=trail)
    second = ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()], audit_trail=trail)

    assert first.manifest.bundle_id == second.manifest.bundle_id
    assert [section.section_id for section in first.sections] == [section.section_id for section in second.sections]


def test_bundle_includes_session_summary() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, audit_trail=trail)

    summary = next(section for section in bundle.sections if section.section_id == "session_summary")
    assert any("session_id:" in item for item in summary.items)


def test_bundle_includes_claim_source_and_audit_sections() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()], audit_trail=trail)
    section_ids = {section.section_id for section in bundle.sections}

    assert {"claim_dockets", "source_dockets", "audit_trail"} <= section_ids


def test_bundle_includes_uncertainty_deferred_unresolved_and_limitations() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()], audit_trail=trail)
    section_ids = {section.section_id for section in bundle.sections}

    assert {"uncertainty", "deferred", "unresolved", "limitations"} <= section_ids
    assert bundle.limitations


def test_formatter_avoids_certainty_inflation() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], source_dockets=[source_docket()], audit_trail=trail)
    result = ReviewBundleFormatter().format(bundle)

    assert result.success
    assert "Review bundles are not final reports." in result.content
    assert "confirmed" not in result.content.casefold()


def test_guardrails_flag_certainty_language() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, audit_trail=trail)
    bundle.sections.append(ReviewBundleSection("bad", "Bad", ["This claim is confirmed."]))

    warnings = ReviewBundleGuardrails().check(bundle)

    assert any(warning.warning_type == "certainty_language" for warning in warnings)


def test_missing_provenance_creates_warning() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(
        session,
        claim_dockets=[claim_docket(with_citation=False)],
        source_dockets=[source_docket(with_citation=False)],
        audit_trail=trail,
    )

    assert any(warning.warning_type == "missing_provenance" for warning in bundle.warnings)


def test_bundle_does_not_mutate_sessions_or_dockets() -> None:
    session, trail = session_and_trail()
    docket = claim_docket()
    before_decisions = len(session.decisions)
    before_text = docket.items[0].canonical_text

    ReviewBundleBuilder().build(session, claim_dockets=[docket], audit_trail=trail)

    assert len(session.decisions) == before_decisions
    assert docket.items[0].canonical_text == before_text


def test_bundle_does_not_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    session, trail = session_and_trail()

    ReviewBundleBuilder().build(session, claim_dockets=[claim_docket()], audit_trail=trail)

    assert graph.edges == {}
