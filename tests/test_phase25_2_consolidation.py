from copy import deepcopy
from pathlib import Path
import re

from roswell_uap_cortex import (
    ClaimMatrixEngine,
    ClaimNode,
    DemoPresentationBuilder,
    DemoWorkspaceBuilder,
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    ReviewInfluencePolicy,
)


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "roswell_uap_cortex"


def test_demo_to_presentation_flow_is_deterministic_and_bounded() -> None:
    first = DemoPresentationBuilder().build()
    second = DemoPresentationBuilder().build()

    assert first == second
    assert first.dashboard.synthetic_only
    assert first.dashboard.claim_cards
    assert first.dashboard.source_cards
    assert first.dashboard.bundle_preview is not None
    assert first.dashboard.session_timeline is not None
    assert first.dashboard.limitations
    assert first.dashboard.provenance_refs


def test_presentation_build_does_not_mutate_demo_session_bundle_or_dockets() -> None:
    result = DemoWorkspaceBuilder().build()
    before = deepcopy(result)

    DemoPresentationBuilder().build(result)

    assert result == before


def test_review_influence_and_presentation_do_not_create_truth_state() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    result = DemoWorkspaceBuilder().build()
    claim = ClaimNode(id="claim-1", text="demo claim", canonical_topic="demo")
    entry = ClaimMatrixEngine().register_unsupported_candidate_topic("demo", claim)
    before = (entry.status, entry.claim_confidence, claim.status, claim.confidence)

    ReviewInfluencePolicy().evaluate(
        result.review_session,
        claim_dockets=[result.claim_review_docket],
        source_dockets=[result.source_review_docket],
    )
    presentation = DemoPresentationBuilder().build(result)

    assert graph.edges == {}
    assert (entry.status, entry.claim_confidence, claim.status, claim.confidence) == before
    assert all(card.confidence_label == "not_truth_confidence" for card in presentation.dashboard.claim_cards)
    assert any(warning.warning_type == "display_not_truth" for warning in presentation.dashboard.warnings)


def test_presentation_contract_preserves_missing_and_unknown_display_boundaries() -> None:
    contract = (ROOT / "docs" / "PRESENTATION_CONTRACT.md").read_text(encoding="utf-8")

    assert "Absent data should remain visibly absent." in contract
    assert "Missing provenance remains missing." in contract
    assert "Unknown source fields remain unknown." in contract
    assert "Grouping is for visual organization only." in contract
    assert "dashboard count is display metadata" in contract


def test_phase_21_to_25_modules_avoid_network_process_and_dynamic_execution_patterns() -> None:
    forbidden = re.compile(
        r"import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system",
        re.IGNORECASE,
    )
    modules = [
        "session_audit.py",
        "session_audit_formatter.py",
        "session_persistence.py",
        "review_bundle.py",
        "review_bundle_formatter.py",
        "review_bundle_guardrails.py",
        "demo_workspace.py",
        "demo_workspace_guardrails.py",
        "review_context.py",
        "review_influence.py",
        "presentation.py",
        "presentation_guardrails.py",
        "demo_presentation.py",
    ]

    offenders = [module for module in modules if forbidden.search((SRC / module).read_text(encoding="utf-8"))]

    assert offenders == []


def test_phase_25_2_consolidation_docs_are_linked() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    security = (ROOT / "docs" / "DEBUGGING_AND_SECURITY.md").read_text(encoding="utf-8")
    maintenance = (ROOT / "docs" / "MAINTENANCE_LOG.md").read_text(encoding="utf-8")

    assert "PHASE_25_2_CONSOLIDATION.md" in readme
    assert "Phase 21-25 Review Workflow And Presentation Check" in security
    assert "Phase 25.2 Review Workflow, Presentation, Debugging, And Security Consolidation" in maintenance
