from copy import deepcopy
from pathlib import Path

from roswell_uap_cortex import (
    DemoPresentationBuilder,
    DemoWorkspaceBuilder,
    GraphNode,
    GraphNodeType,
    PresentationGuardrails,
    PresentationWarning,
    RelationshipGraphEngine,
    ReviewDashboardView,
)


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_demo_presentation_builds_deterministically() -> None:
    first = DemoPresentationBuilder().build()
    second = DemoPresentationBuilder().build()

    assert first == second
    assert first.demo_id == second.demo_id
    assert first.dashboard.title == "Synthetic Cortex Demo Workspace"


def test_demo_presentation_preserves_synthetic_label_and_limitations() -> None:
    presentation = DemoPresentationBuilder().build()

    assert presentation.dashboard.synthetic_only
    assert presentation.dashboard.limitations
    assert any("not final reports" in item for item in presentation.dashboard.limitations)
    assert any("synthetic" in note for note in presentation.boundary_notes)


def test_claim_cards_keep_unsupported_and_priority_not_truth() -> None:
    presentation = DemoPresentationBuilder().build()

    assert presentation.dashboard.claim_cards
    assert all(card.unsupported for card in presentation.dashboard.claim_cards)
    assert all(card.confidence_label == "not_truth_confidence" for card in presentation.dashboard.claim_cards)
    assert any("display priority is not truth confidence" in note for card in presentation.dashboard.claim_cards for note in card.notes)


def test_source_cards_keep_risk_as_warning_not_rejection() -> None:
    presentation = DemoPresentationBuilder().build()

    assert presentation.dashboard.source_cards
    risk_cards = [card for card in presentation.dashboard.source_cards if card.risk_score > 0.0]
    assert risk_cards
    assert any(
        warning.warning_type == "source_risk_not_rejection"
        for card in risk_cards
        for warning in card.warnings
    )
    assert not any("rejected" in " ".join(card.notes).casefold() for card in presentation.dashboard.source_cards)


def test_contradictions_deferred_uncertainty_and_provenance_remain_visible() -> None:
    presentation = DemoPresentationBuilder().build()
    dashboard = presentation.dashboard

    assert dashboard.contradiction_ids
    assert dashboard.unresolved_ids
    assert dashboard.uncertainty_notes
    assert dashboard.provenance_refs
    assert dashboard.session_timeline is not None
    assert dashboard.session_timeline.unresolved_ids


def test_bundle_preview_and_audit_timeline_are_display_only() -> None:
    presentation = DemoPresentationBuilder().build()

    assert presentation.dashboard.bundle_preview is not None
    assert presentation.dashboard.bundle_preview.section_titles
    assert presentation.dashboard.session_timeline is not None
    assert any(
        warning.warning_type == "audit_not_evidence"
        for warning in presentation.dashboard.session_timeline.warnings
    )
    assert "Cortex Review Bundle" in presentation.formatted_bundle_preview


def test_presentation_does_not_mutate_demo_result() -> None:
    result = DemoWorkspaceBuilder().build()
    before = deepcopy(result)

    DemoPresentationBuilder().build(result)

    assert result == before


def test_presentation_does_not_create_graph_edges_or_decisions() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="demo"))
    result = DemoWorkspaceBuilder().build()
    decision_count = len(result.review_session.decisions)

    DemoPresentationBuilder().build(result)

    assert graph.edges == {}
    assert len(result.review_session.decisions) == decision_count


def test_presentation_guardrails_warn_on_certainty_language() -> None:
    dashboard = ReviewDashboardView(
        title="Confirmed finding",
        synthetic_only=True,
        provenance_refs={"prov-1"},
        limitations=["Review presentation is not a final report."],
    )

    warnings = PresentationGuardrails().check(dashboard)

    assert any(warning.warning_type == "certainty_language" for warning in warnings)
    assert any(warning.warning_type == "display_not_truth" for warning in warnings)


def test_presentation_guardrails_require_synthetic_label_limitations_and_provenance() -> None:
    dashboard = ReviewDashboardView(title="Demo", synthetic_only=False)

    warnings = PresentationGuardrails().check(dashboard)
    warning_types = {warning.warning_type for warning in warnings}

    assert "missing_synthetic_label" in warning_types
    assert "missing_limitations" in warning_types
    assert "missing_provenance" in warning_types


def test_presentation_warning_is_plain_display_metadata() -> None:
    warning = PresentationWarning("display_not_truth", "display only", {"id-1"})

    assert warning.warning_type == "display_not_truth"
    assert warning.related_ids == {"id-1"}


def test_presentation_contract_is_documented_and_linked() -> None:
    contract = read("docs/PRESENTATION_CONTRACT.md")

    for phrase in [
        "Presentation may arrange review state for display.",
        "Presentation should stay boring",
        "Presentation must not:",
        "No Aggregation Semantics",
        "Absent Data",
        "DemoPresentation",
        "ReviewDashboardView",
        "create graph edges",
        "turn review bundles into final reports",
        "Multiple claim cards grouped by topic do not imply corroboration.",
        "Missing provenance remains missing.",
    ]:
        assert phrase in contract

    for path in [
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/WORKFLOW_MAP.md",
        "docs/UI_READINESS_NOTES.md",
        "docs/AI_DEBT.md",
    ]:
        assert "PRESENTATION_CONTRACT.md" in read(path) or "Presentation Contract Debt" in read(path)


def test_presentation_debt_tracks_boring_contract_and_future_view_types() -> None:
    text = read("docs/AI_DEBT.md")

    assert "Keep presentation contracts boring" in text
    assert "grouped cards" in text
    assert "dashboard counts" in text
    assert "ProvenanceReferenceView" in text
    assert "UncertaintyPanelView" in text
    assert "ContradictionPanelView" in text
