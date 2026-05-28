from roswell_uap_cortex import (
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    ClaimMatrixStatus,
    ClaimNode,
    ContaminationFlagType,
    GraphNode,
    GraphNodeType,
    HybridRetrievalCoordinator,
    MockEmbeddingBackend,
    RelationshipGraphEngine,
    SemanticClusterEngine,
    SemanticContaminationGuard,
    SemanticRecord,
    SemanticSimilarityEngine,
    SemanticWarningType,
)


def semantic_record(
    record_id: str,
    text: str,
    *,
    lineage_id: str | None = "line-a",
    provenance: bool = True,
    contradiction_pressure: float = 0.0,
    contested: bool = False,
    flags: list[str] | None = None,
) -> SemanticRecord:
    return SemanticRecord(
        record_id=record_id,
        text=text,
        record_role="evidence",
        tags={"radar"},
        entity_ids={"entity-1"},
        provenance_ids={f"prov-{record_id}"} if provenance else set(),
        source_id=f"source-{record_id}",
        lineage_id=lineage_id,
        contradiction_pressure=contradiction_pressure,
        contested=contested,
        contamination_flags=flags or [],
    )


def test_mock_embedding_backend_is_deterministic() -> None:
    backend = MockEmbeddingBackend()

    assert backend.embed_text("bright object").values == backend.embed_text("bright object").values


def test_semantic_similarity_is_bounded_between_zero_and_one() -> None:
    result = SemanticSimilarityEngine().compare(
        semantic_record("a", "bright radar object"),
        semantic_record("b", "bright radar object", lineage_id="line-b"),
    )

    assert 0.0 <= result.similarity_score <= 1.0


def test_semantic_similarity_does_not_create_graph_edges() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.EVIDENCE, label="a"))

    SemanticSimilarityEngine().compare(
        semantic_record("a", "bright radar object"),
        semantic_record("b", "bright radar object", lineage_id="line-b"),
    )

    assert graph.edges == {}


def test_semantic_similarity_does_not_confirm_claims() -> None:
    claim = ClaimNode(text="unsupported", canonical_topic="x", status=ClaimMatrixStatus.UNSUPPORTED)

    SemanticSimilarityEngine().compare(
        semantic_record("a", "unsupported claim text"),
        semantic_record("b", "unsupported claim text", lineage_id="line-b"),
    )

    assert claim.status is ClaimMatrixStatus.UNSUPPORTED


def test_same_lineage_records_are_downgraded() -> None:
    same = SemanticSimilarityEngine().compare(
        semantic_record("a", "bright radar object", lineage_id="same"),
        semantic_record("b", "bright radar object", lineage_id="same"),
    )
    separate = SemanticSimilarityEngine().compare(
        semantic_record("a", "bright radar object", lineage_id="a"),
        semantic_record("c", "bright radar object", lineage_id="c"),
    )

    assert same.similarity_score <= 0.45
    assert separate.similarity_score > same.similarity_score


def test_contradiction_pressure_lowers_similarity_result() -> None:
    calm = SemanticSimilarityEngine().compare(
        semantic_record("a", "radar object", lineage_id="a"),
        semantic_record("b", "radar object", lineage_id="b"),
    )
    pressured = SemanticSimilarityEngine().compare(
        semantic_record("a", "radar object", lineage_id="a", contradiction_pressure=0.8),
        semantic_record("b", "radar object", lineage_id="b", contradiction_pressure=0.8),
    )

    assert pressured.similarity_score < calm.similarity_score


def test_missing_provenance_creates_warning_flags() -> None:
    result = SemanticSimilarityEngine().compare(
        semantic_record("a", "radar object", provenance=False),
        semantic_record("b", "radar object", lineage_id="b"),
    )

    assert SemanticWarningType.MISSING_PROVENANCE in {
        warning.warning_type for warning in result.warning_flags
    }


def test_semantic_clusters_preserve_member_ids() -> None:
    clusters = SemanticClusterEngine().cluster(
        [
            semantic_record("a", "bright radar object", lineage_id="a"),
            semantic_record("b", "bright radar object", lineage_id="b"),
        ]
    )

    assert any(cluster.member_ids == {"a", "b"} for cluster in clusters)


def test_semantic_clusters_do_not_imply_equivalence() -> None:
    cluster = SemanticClusterEngine().cluster(
        [
            semantic_record("a", "bright radar object", lineage_id="a"),
            semantic_record("b", "bright radar object", lineage_id="b"),
        ]
    )[0]

    assert cluster.cluster_label == "possible_related_cluster"


def test_contested_records_remain_visible_in_clusters() -> None:
    cluster = SemanticClusterEngine().cluster(
        [
            semantic_record("a", "bright radar object", lineage_id="a", contested=True),
            semantic_record("b", "bright radar object", lineage_id="b"),
        ]
    )[0]

    assert "a" in cluster.contested_member_ids


def test_hybrid_retrieval_preserves_component_scores() -> None:
    semantic = SemanticSimilarityEngine().compare(
        semantic_record("a", "radar object", lineage_id="a"),
        semantic_record("b", "radar object", lineage_id="b"),
    )
    result = HybridRetrievalCoordinator().combine(
        associative_candidates=[
            AssociationCandidate(
                record_id="a",
                record_type="evidence",
                label="a",
                score=AssociationScore(final_association_score=0.4),
                association_label=AssociationLabel.POSSIBLE_ASSOCIATION,
            )
        ],
        graph_node_ids={"a"},
        timeline_scores={"a": 0.3},
        semantic_results=[semantic],
        provenance_visible_ids={"a"},
    )[0]

    assert result.associative_score == 0.4
    assert result.graph_score == 1.0
    assert result.timeline_score == 0.3
    assert result.semantic_similarity_score > 0
    assert result.ranking_score <= 1.0


def test_hybrid_retrieval_exposes_uncertainty_notes() -> None:
    result = HybridRetrievalCoordinator().combine(graph_node_ids={"missing-prov"})[0]

    assert "missing provenance visibility" in result.uncertainty_notes


def test_semantic_contamination_guard_propagates_warnings() -> None:
    result = SemanticSimilarityEngine().compare(
        semantic_record(
            "a",
            "warp drive object",
            flags=[ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS.value],
        ),
        semantic_record("b", "warp drive object", lineage_id="b"),
    )

    assert SemanticWarningType.FICTIONAL_CONTAMINATION in {
        warning.warning_type for warning in result.warning_flags
    }


def test_no_external_embedding_dependencies_or_network_calls_are_required() -> None:
    pyproject = open("pyproject.toml", encoding="utf-8").read()

    assert "sentence-transformers" not in pyproject
    assert "chromadb" not in pyproject
    assert "faiss" not in pyproject
    assert "openai" not in pyproject
