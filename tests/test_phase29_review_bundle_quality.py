from roswell_uap_cortex import (
    ClaimReviewDocket,
    ClaimReviewItem,
    DiscourseCitation,
    EvidenceAssessmentSummary,
    EvidenceQualityLabel,
    EvidenceQualitySummary,
    EvidenceQualityWarningType,
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


def quality_summary(
    evidence_id: str = "e-quality",
    *,
    label: EvidenceQualityLabel = EvidenceQualityLabel.FRAGILE,
) -> EvidenceQualitySummary:
    return EvidenceQualitySummary(
        evidence_id=evidence_id,
        quality_label=label,
        quality_score=0.48 if label is EvidenceQualityLabel.FRAGILE else 0.82,
        review_priority_score=0.72 if label is EvidenceQualityLabel.FRAGILE else 0.12,
        weak_dimensions=["provenance_completeness", "lineage_clarity"] if label is EvidenceQualityLabel.FRAGILE else [],
        warning_types=[
            EvidenceQualityWarningType.QUALITY_NOT_TRUTH,
            EvidenceQualityWarningType.REVIEW_SIGNAL_ONLY,
            EvidenceQualityWarningType.MISSING_PROVENANCE,
        ],
        reason_codes=["missing_provenance"],
    )


def claim_docket_with_quality() -> ClaimReviewDocket:
    item = ClaimReviewItem(
        normalized_claim_id="claim-quality",
        canonical_topic="quality-topic",
        canonical_text="observer saw bright light",
        priority=ReviewPriority.HIGH,
        priority_score=0.7,
        support_summaries=[EvidenceAssessmentSummary("e-quality", "possible_support", support_score=0.6)],
        quality_summaries=[quality_summary()],
    )
    return ClaimReviewDocket(
        "claim-docket-quality",
        "Claim Docket Quality",
        items=[item],
        citations=[DiscourseCitation(evidence_id="e-quality", provenance_id="p-quality", label="quality citation")],
    )


def source_docket_with_quality() -> SourceReviewDocket:
    item = SourceReviewItem(
        source_id="fixture://source-quality",
        priority=SourceReviewPriority.HIGH,
        priority_score=0.7,
        risk_score=0.5,
        reliability_score=0.4,
        evidence_ids={"e-quality"},
        quality_summaries=[quality_summary()],
        notes=["source review item only; evidence quality is review context, not source truth"],
    )
    return SourceReviewDocket(
        "source-docket-quality",
        "Source Docket Quality",
        items=[item],
        citations=[DiscourseCitation(evidence_id="e-quality", source_id="fixture://source-quality", provenance_id="p-quality", label="source quality citation")],
    )


def session_and_trail():
    state = WorkingMemoryEngine().build_state(
        query="quality bundle",
        claim_dockets=[claim_docket_with_quality()],
        source_dockets=[source_docket_with_quality()],
    )
    session = ReviewSessionEngine().start_session("Quality Bundle Session", state)
    ReviewSessionEngine().record_decision(
        session,
        item_id="claim-quality",
        item_type="claim",
        decision_type=ReviewDecisionType.DEFERRED,
        notes=["needs quality-aware review"],
    )
    logger = SessionAuditLogger()
    return session, logger.build_trail(session, [logger.start(session), logger.decision(session, session.decisions[-1])])


def build_bundle():
    session, trail = session_and_trail()
    return ReviewBundleBuilder().build(
        session,
        claim_dockets=[claim_docket_with_quality()],
        source_dockets=[source_docket_with_quality()],
        audit_trail=trail,
    )


def test_review_bundle_includes_evidence_quality_section() -> None:
    bundle = build_bundle()
    section = next(section for section in bundle.sections if section.section_id == "evidence_quality")

    assert section.title == "Evidence Quality"
    assert any("evidence:e-quality" in item for item in section.items)
    assert any("label=fragile" in item for item in section.items)
    assert any("weak_dimensions=lineage_clarity, provenance_completeness" in item for item in section.items)


def test_quality_section_has_review_context_boundary() -> None:
    bundle = build_bundle()
    section = next(section for section in bundle.sections if section.section_id == "evidence_quality")

    assert "boundary:evidence quality is review context, not claim confirmation or source truth" in section.items
    assert not any(warning.warning_type == "missing_quality_boundary" for warning in bundle.warnings)


def test_review_bundle_formatter_preserves_quality_without_certainty_language() -> None:
    result = ReviewBundleFormatter().format(build_bundle())

    assert result.success
    assert "## Evidence Quality" in result.content
    assert "quality_score=0.48" in result.content
    assert "not claim confirmation or source truth" in result.content
    assert "confirmed" not in result.content.casefold()


def test_quality_section_does_not_create_final_report_or_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.EVIDENCE, label="evidence"))

    bundle = build_bundle()

    assert "Review bundles are not final reports." in bundle.limitations
    assert graph.edges == {}


def test_bundle_guardrails_warn_when_quality_boundary_is_missing() -> None:
    bundle = build_bundle()
    quality = next(section for section in bundle.sections if section.section_id == "evidence_quality")
    quality.items = [item for item in quality.items if not item.startswith("boundary:")]

    warnings = ReviewBundleGuardrails().check(bundle)

    assert any(warning.warning_type == "missing_quality_boundary" for warning in warnings)


def test_empty_quality_section_remains_bounded() -> None:
    session, trail = session_and_trail()
    bundle = ReviewBundleBuilder().build(session, audit_trail=trail)
    section = next(section for section in bundle.sections if section.section_id == "evidence_quality")

    assert section.items == ["none"]
    assert not any(warning.warning_type == "missing_quality_boundary" for warning in bundle.warnings)
