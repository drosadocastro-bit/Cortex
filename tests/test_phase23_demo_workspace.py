from roswell_uap_cortex import (
    ClaimEvidenceAssessmentType,
    ContaminationFlagType,
    DemoWorkspaceBuilder,
    DemoWorkspaceGuardrails,
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    ReviewBundleFormatter,
)


def test_demo_workspace_builds_deterministically() -> None:
    first = DemoWorkspaceBuilder().build()
    second = DemoWorkspaceBuilder().build()

    assert first.workspace.manifest.demo_id == second.workspace.manifest.demo_id
    assert first.review_bundle.manifest.bundle_id == second.review_bundle.manifest.bundle_id
    assert first.formatted_bundle == second.formatted_bundle


def test_demo_workspace_uses_synthetic_only_source_ids() -> None:
    result = DemoWorkspaceBuilder().build()

    assert result.workspace.manifest.synthetic_only
    for raw in result.workspace.raw_inputs:
        source = raw.source_uri or f"unknown:{raw.input_id}"
        assert source.startswith(("synthetic://", "unknown:"))


def test_demo_workspace_produces_evidence_provenance_and_lineage() -> None:
    result = DemoWorkspaceBuilder().build()

    assert sum(len(item.evidence_items) for item in result.ingestion_results) >= 5
    assert all(item.provenance_records for item in result.ingestion_results)
    assert all(item.lineage_records for item in result.ingestion_results)


def test_demo_workspace_produces_candidate_and_normalized_claims() -> None:
    result = DemoWorkspaceBuilder().build()

    assert result.candidate_claims
    assert result.normalized_claims
    assert all(claim.unsupported for claim in result.normalized_claims)


def test_demo_workspace_produces_claim_and_source_dockets() -> None:
    result = DemoWorkspaceBuilder().build()

    assert result.claim_review_docket is not None
    assert result.claim_review_docket.items
    assert result.source_review_docket is not None
    assert result.source_review_docket.items


def test_demo_workspace_produces_session_audit_and_bundle() -> None:
    result = DemoWorkspaceBuilder().build()

    assert result.review_session is not None
    assert result.audit_trail is not None
    assert result.audit_trail.records
    assert result.review_bundle is not None
    assert "Cortex Review Bundle" in result.formatted_bundle


def test_demo_workspace_includes_contradiction() -> None:
    result = DemoWorkspaceBuilder().build()

    assert any(
        assessment.assessment_type
        in {ClaimEvidenceAssessmentType.POSSIBLE_CONTRADICTION, ClaimEvidenceAssessmentType.NEEDS_REVIEW}
        for assessment in result.claim_evaluation.assessments
    )
    assert result.review_session.state.contradiction_ids


def test_demo_workspace_includes_uncertainty_and_provenance_warning() -> None:
    result = DemoWorkspaceBuilder().build()
    flags = {flag.flag_type for ingestion in result.ingestion_results for flag in ingestion.contamination_flags}

    assert ContaminationFlagType.MISSING_SOURCE_URI in flags
    assert result.review_session.state.uncertainty_notes


def test_demo_workspace_contains_contamination_and_derivative_source() -> None:
    result = DemoWorkspaceBuilder().build()
    flags = {flag.flag_type for ingestion in result.ingestion_results for flag in ingestion.contamination_flags}
    lineage_notes = [record for ingestion in result.ingestion_results for record in ingestion.lineage_records]

    assert ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS in flags
    assert any(record.parent_source_id == "synthetic://demo-primary" for record in lineage_notes)


def test_demo_workspace_guardrails_reject_non_synthetic_source() -> None:
    workspace = DemoWorkspaceBuilder().synthetic_workspace()
    workspace.raw_inputs[0].source_uri = "https://example.com/real"

    try:
        DemoWorkspaceGuardrails().validate_workspace(workspace)
    except ValueError as exc:
        assert "not synthetic" in str(exc)
    else:
        raise AssertionError("non-synthetic demo source was accepted")


def test_demo_workspace_does_not_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.EVIDENCE, label="demo"))

    DemoWorkspaceBuilder().build()

    assert graph.edges == {}


def test_bundle_formatter_works_on_demo_output() -> None:
    result = DemoWorkspaceBuilder().build()
    export = ReviewBundleFormatter().format(result.review_bundle)

    assert export.success
    assert "Review bundles are not final reports." in export.content
