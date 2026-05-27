from datetime import date

from roswell_uap_cortex import (
    ClaimEvidenceContribution,
    ClaimMatrixEngine,
    ClaimMatrixStatus,
    ClaimNode,
    EntityNode,
    EventNode,
    RelationshipEdge,
    RelationshipGraphEngine,
    RelationshipType,
    SourceNode,
    TimelineDatePrecision,
    TimelineEngine,
)


def contribution(
    evidence_id: str,
    source_id: str,
    *,
    lineage_id: str | None = None,
    confidence: float = 0.8,
    source_trust: float = 0.8,
    source_kind: str = "archival_document",
) -> ClaimEvidenceContribution:
    return ClaimEvidenceContribution(
        evidence_id=evidence_id,
        source_id=source_id,
        lineage_id=lineage_id,
        confidence=confidence,
        source_trust=source_trust,
        source_kind=source_kind,
    )


def test_timeline_orders_exact_dates_correctly() -> None:
    engine = TimelineEngine()
    later = engine.add_event(EventNode(label="later", event_date=date(1947, 7, 8)))
    earlier = engine.add_event(EventNode(label="earlier", event_date=date(1947, 7, 4)))
    middle = engine.add_event(EventNode(label="middle", event_date=date(1947, 7, 6)))

    assert [event.id for event in engine.ordered_events()] == [earlier.id, middle.id, later.id]
    assert [event.id for event in engine.events_before(later.id)] == [earlier.id, middle.id]
    assert [event.id for event in engine.events_after(earlier.id)] == [middle.id, later.id]


def test_timeline_preserves_approximate_and_unknown_dates_without_fabrication() -> None:
    engine = TimelineEngine()
    approximate = engine.add_event(
        EventNode(
            label="approximate",
            earliest_possible_date=date(1947, 7, 1),
            latest_possible_date=date(1947, 7, 31),
            date_precision=TimelineDatePrecision.APPROXIMATE,
            date_note="sometime in July",
        )
    )
    unknown = engine.add_event(EventNode(label="unknown"))

    ordered = engine.ordered_events()

    assert ordered[0] is approximate
    assert ordered[-1] is unknown
    assert approximate.event_date is None
    assert unknown.event_date is None
    assert engine.events_before(unknown.id) == []
    assert unknown.date_precision is TimelineDatePrecision.UNKNOWN


def test_claim_matrix_separates_support_from_contradiction() -> None:
    engine = ClaimMatrixEngine()
    entry = engine.add_claim(ClaimNode(text="event happened", canonical_topic="event-date"))

    engine.add_support("event-date", contribution("support-1", "archive", lineage_id="line-a"))
    entry = engine.add_contradiction(
        "event-date",
        contribution("contra-1", "memo", lineage_id="line-b", confidence=0.7),
    )

    assert [item.evidence_id for item in entry.supporting_evidence] == ["support-1"]
    assert [item.evidence_id for item in entry.contradicting_evidence] == ["contra-1"]
    assert entry.claims[0].status is ClaimMatrixStatus.CONTESTED


def test_repeated_same_lineage_evidence_does_not_inflate_confidence() -> None:
    duplicate_engine = ClaimMatrixEngine()
    duplicate_engine.add_support(
        "material-origin",
        contribution("dup-1", "archive", lineage_id="same-line"),
    )
    duplicate_entry = duplicate_engine.add_support(
        "material-origin",
        contribution("dup-2", "book-retelling", lineage_id="same-line"),
    )

    single_engine = ClaimMatrixEngine()
    single_entry = single_engine.add_support(
        "material-origin",
        contribution("single-1", "archive", lineage_id="same-line"),
    )

    assert duplicate_entry.claim_confidence <= single_entry.claim_confidence + 0.06


def test_independent_sources_increase_confidence_more_than_duplicates() -> None:
    duplicate_engine = ClaimMatrixEngine()
    duplicate_engine.add_support("radar", contribution("dup-1", "archive", lineage_id="same"))
    duplicate_entry = duplicate_engine.add_support(
        "radar",
        contribution("dup-2", "reprint", lineage_id="same"),
    )

    independent_engine = ClaimMatrixEngine()
    independent_engine.add_support("radar", contribution("ind-1", "archive", lineage_id="a"))
    independent_entry = independent_engine.add_support(
        "radar",
        contribution("ind-2", "transcript", lineage_id="b", source_kind="transcript"),
    )

    assert independent_entry.claim_confidence > duplicate_entry.claim_confidence


def test_contested_claims_are_labeled_contested() -> None:
    engine = ClaimMatrixEngine()
    engine.add_support("location", contribution("support", "archive", lineage_id="a"))
    entry = engine.add_contradiction(
        "location",
        contribution("contra", "witness", lineage_id="b", source_kind="witness"),
    )

    assert entry.status is ClaimMatrixStatus.CONTESTED


def test_unsupported_claims_remain_unsupported() -> None:
    engine = ClaimMatrixEngine()
    entry = engine.add_claim(ClaimNode(text="unsupported assertion", canonical_topic="unsupported"))

    assert entry.status is ClaimMatrixStatus.UNSUPPORTED
    assert entry.claim_confidence == 0.0


def test_graph_prevents_duplicate_edges() -> None:
    graph = RelationshipGraphEngine()
    claim = graph.add_node(ClaimNode(text="claim", canonical_topic="topic"))
    source = graph.add_node(SourceNode(source_id="archive", label="Archive"))

    first = graph.add_edge(
        RelationshipEdge(
            from_node_id=source.id,
            to_node_id=claim.id,
            relation=RelationshipType.SUPPORTS,
            source_id="archive",
            evidence_ids={"e1"},
        )
    )
    second = graph.add_edge(
        RelationshipEdge(
            from_node_id=source.id,
            to_node_id=claim.id,
            relation=RelationshipType.SUPPORTS,
            source_id="archive",
            evidence_ids={"e2"},
            confidence=0.8,
        )
    )

    assert first is second
    assert len(graph.edges) == 1
    assert first.evidence_ids == {"e1", "e2"}
    assert first.confidence == 0.8


def test_graph_retrieves_contradiction_relationships() -> None:
    graph = RelationshipGraphEngine()
    first = graph.add_node(ClaimNode(text="before midnight", canonical_topic="time"))
    second = graph.add_node(ClaimNode(text="after midnight", canonical_topic="time"))
    edge = graph.add_edge(
        RelationshipEdge(
            from_node_id=first.id,
            to_node_id=second.id,
            relation=RelationshipType.CONTRADICTS,
            source_id="analysis",
            evidence_ids={"e1", "e2"},
        )
    )

    assert graph.contradiction_edges(first.id) == [edge]
    assert graph.neighbors(first.id, relation=RelationshipType.CONTRADICTS) == [second]


def test_graph_neighborhood_returns_relevant_connected_nodes() -> None:
    graph = RelationshipGraphEngine()
    claim = graph.add_node(ClaimNode(text="claim", canonical_topic="topic"))
    entity = graph.add_node(EntityNode(label="Entity"))
    source = graph.add_node(SourceNode(source_id="source", label="Source"))
    graph.add_edge(
        RelationshipEdge(
            from_node_id=source.id,
            to_node_id=claim.id,
            relation=RelationshipType.SUPPORTS,
            source_id="source",
        )
    )
    graph.add_edge(
        RelationshipEdge(
            from_node_id=claim.id,
            to_node_id=entity.id,
            relation=RelationshipType.MENTIONS,
            source_id="source",
        )
    )

    neighborhood = graph.neighborhood(claim.id, depth=1)

    assert set(neighborhood.nodes) == {claim.id, source.id, entity.id}
    assert len(neighborhood.edges) == 2


def test_source_lineage_chains_can_be_traced() -> None:
    graph = RelationshipGraphEngine()
    video = graph.add_node(SourceNode(source_id="video", label="Video"))
    book = graph.add_node(SourceNode(source_id="book", label="Book"))
    archive = graph.add_node(SourceNode(source_id="archive", label="Archive"))
    graph.add_edge(
        RelationshipEdge(
            from_node_id=video.id,
            to_node_id=book.id,
            relation=RelationshipType.DERIVED_FROM,
            source_id="lineage",
        )
    )
    graph.add_edge(
        RelationshipEdge(
            from_node_id=book.id,
            to_node_id=archive.id,
            relation=RelationshipType.DERIVED_FROM,
            source_id="lineage",
        )
    )

    assert graph.source_lineage_chain(video.id) == [video.id, book.id, archive.id]
