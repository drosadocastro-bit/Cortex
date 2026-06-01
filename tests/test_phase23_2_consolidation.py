from pathlib import Path
import re

from roswell_uap_cortex import (
    DemoWorkspaceBuilder,
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    ReviewBundleGuardrails,
    ReviewBundleSection,
    ReviewDecisionType,
    ReviewSessionEngine,
    SessionPersistenceStore,
    WorkingMemoryEngine,
)


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "roswell_uap_cortex"


def test_demo_bundle_limitations_always_present() -> None:
    result = DemoWorkspaceBuilder().build()
    section_ids = {section.section_id for section in result.review_bundle.sections}

    assert "limitations" in section_ids
    assert result.review_bundle.limitations
    assert "Review bundles are not final reports." in result.formatted_bundle


def test_demo_workspace_never_contains_non_synthetic_sources() -> None:
    result = DemoWorkspaceBuilder().build()

    assert result.workspace.manifest.synthetic_only
    for raw_input in result.workspace.raw_inputs:
        source = raw_input.source_uri or f"unknown:{raw_input.input_id}"
        assert source.startswith(("synthetic://", "unknown:"))


def test_session_persistence_load_does_not_apply_decisions_to_graph() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    session = ReviewSessionEngine().start_session("Consolidation", WorkingMemoryEngine().build_state())
    ReviewSessionEngine().record_decision(
        session,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.REVIEWED,
    )
    store = SessionPersistenceStore()
    envelope = store.build_envelope([session], [])
    loaded_envelope = store._envelope_from_payload(store.serializer.to_json_compatible(envelope))
    errors, _ = store.validate(loaded_envelope)

    assert errors == []
    assert graph.edges == {}
    assert loaded_envelope.sessions[0].decisions[0].decision_type is ReviewDecisionType.REVIEWED


def test_review_bundle_guardrails_do_not_overtrigger_on_provenance() -> None:
    bundle = DemoWorkspaceBuilder().build().review_bundle
    bundle.sections.append(
        ReviewBundleSection(
            "provenance_note",
            "Provenance Note",
            ["Provenance remains visible and bounded."],
        )
    )

    warnings = ReviewBundleGuardrails().check(bundle)

    assert not any(warning.warning_type == "certainty_language" for warning in warnings)


def test_phase_19_to_23_modules_avoid_network_process_and_dynamic_execution_patterns() -> None:
    forbidden = re.compile(
        r"import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system",
        re.IGNORECASE,
    )
    modules = [
        "source_review.py",
        "source_risk.py",
        "working_memory.py",
        "review_session.py",
        "session_persistence.py",
        "session_audit.py",
        "review_bundle.py",
        "review_bundle_guardrails.py",
        "demo_workspace.py",
        "demo_workspace_guardrails.py",
    ]

    offenders = [module for module in modules if forbidden.search((SRC / module).read_text(encoding="utf-8"))]

    assert offenders == []
