from copy import deepcopy
from datetime import date

from roswell_uap_cortex import (
    EventNode,
    EvidenceItem,
    NetworkXGraphBackend,
    RelationshipEdge,
    RelationshipType,
    TemporalReasoningHelper,
    TimelineDatePrecision,
    TimelineEngine,
)


def edge(
    from_node: str,
    to_node: str,
    relation: RelationshipType,
    *,
    source_id: str = "source",
    evidence_ids: set[str] | None = None,
) -> RelationshipEdge:
    return RelationshipEdge(
        from_node_id=from_node,
        to_node_id=to_node,
        relation=relation,
        source_id=source_id,
        evidence_ids=evidence_ids or set(),
    )


def test_networkx_backend_preserves_deterministic_traversal() -> None:
    backend = NetworkXGraphBackend()
    for node_id in ["c", "a", "b"]:
        backend.add_node(node_id)
    backend.add_edge(edge("a", "c", RelationshipType.MENTIONS))
    backend.add_edge(edge("a", "b", RelationshipType.MENTIONS))

    assert backend.get_neighbors("a") == ["b", "c"]
    assert backend.get_neighbors("a") == ["b", "c"]


def test_duplicate_edges_remain_deduplicated() -> None:
    backend = NetworkXGraphBackend()
    first = backend.add_edge(edge("a", "b", RelationshipType.SUPPORTS, evidence_ids={"e1"}))
    second = backend.add_edge(edge("a", "b", RelationshipType.SUPPORTS, evidence_ids={"e2"}))

    assert first is second
    assert len(backend.edges_by_key) == 1
    assert first.evidence_ids == {"e1", "e2"}


def test_contradiction_traversal_works() -> None:
    backend = NetworkXGraphBackend()
    contradiction = backend.add_edge(edge("claim-a", "claim-b", RelationshipType.CONTRADICTS))

    assert backend.get_contradictions("claim-a") == [contradiction]


def test_lineage_traversal_works() -> None:
    backend = NetworkXGraphBackend()
    backend.add_edge(edge("video", "book", RelationshipType.DERIVED_FROM))
    backend.add_edge(edge("book", "archive", RelationshipType.DERIVED_FROM))

    assert backend.get_lineage_paths("video") == [["video", "book", "archive"]]


def test_subgraph_extraction_works() -> None:
    backend = NetworkXGraphBackend()
    backend.add_edge(edge("a", "b", RelationshipType.MENTIONS))
    backend.add_edge(edge("b", "c", RelationshipType.MENTIONS))

    result = backend.subgraph("a", depth=1)

    assert result.node_ids == ["a", "b"]
    assert len(result.edges) == 1


def test_timeline_ordering_remains_deterministic() -> None:
    engine = TimelineEngine()
    engine.add_event(EventNode(id="later", label="later", event_date=date(1947, 7, 8)))
    engine.add_event(EventNode(id="earlier", label="earlier", event_date=date(1947, 7, 1)))

    assert [event.id for event in engine.ordered_events()] == ["earlier", "later"]


def test_fuzzy_dates_preserve_uncertainty() -> None:
    event = TimelineEngine().event_from_date_hint(label="month hint", date_hint="July 1947")

    assert event.event_date is None
    assert event.date_precision is TimelineDatePrecision.APPROXIMATE
    assert event.earliest_possible_date == date(1947, 7, 1)
    assert event.latest_possible_date == date(1947, 7, 31)


def test_impossible_temporal_ordering_is_detected() -> None:
    helper = TemporalReasoningHelper()
    later = EventNode(label="later", event_date=date(1947, 7, 10))
    earlier = EventNode(label="earlier", event_date=date(1947, 7, 1))

    assert helper.detect_impossible_sequence(later, earlier) is True


def test_approximate_dates_do_not_become_exact_dates() -> None:
    event = TimelineEngine().event_from_date_hint(label="year hint", date_hint="1947")

    assert event.event_date is None
    assert event.date_precision is TimelineDatePrecision.YEAR
    assert event.earliest_possible_date == date(1947, 1, 1)
    assert event.latest_possible_date == date(1947, 12, 31)


def test_graph_backend_does_not_mutate_evidence() -> None:
    evidence = EvidenceItem(summary="immutable", source_id="s", evidence_type="note")
    before = deepcopy(evidence)
    backend = NetworkXGraphBackend()
    backend.add_edge(edge("a", "b", RelationshipType.REFERENCES, evidence_ids={evidence.id}))

    assert evidence == before


def test_provenance_metadata_survives_traversal() -> None:
    backend = NetworkXGraphBackend()
    backend.add_node("a", source_uri="synthetic://a")
    backend.add_node("b", source_uri="synthetic://b")
    backend.add_edge(edge("a", "b", RelationshipType.REFERENCES, evidence_ids={"e1"}))

    result = backend.subgraph("a", depth=1)

    assert result.edges[0].evidence_ids == {"e1"}
    assert backend.graph.nodes["a"]["source_uri"] == "synthetic://a"


def test_all_graph_operations_remain_deterministic() -> None:
    backend = NetworkXGraphBackend()
    backend.add_edge(edge("a", "c", RelationshipType.MENTIONS))
    backend.add_edge(edge("a", "b", RelationshipType.MENTIONS))

    first = backend.subgraph("a", depth=1)
    second = backend.subgraph("a", depth=1)

    assert first.node_ids == second.node_ids
    assert [item.id for item in first.edges] == [item.id for item in second.edges]


def test_previous_epistemic_guardrails_still_hold() -> None:
    event = TimelineEngine().event_from_date_hint(label="unknown", date_hint="unknown")

    assert event.date_precision is TimelineDatePrecision.UNKNOWN
    assert event.event_date is None
