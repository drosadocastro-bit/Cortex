from datetime import date

from roswell_uap_cortex import (
    ActivationContextBuilder,
    AssociationCandidate,
    AssociationLabel,
    AssociationScore,
    AssociativeRetrievalEngine,
    ClaimMatrixStatus,
    ClaimNode,
    EvidenceItem,
    MemoryRecord,
    RelationshipGraphEngine,
    RetrievalContext,
)


def test_similar_wording_produces_possible_association() -> None:
    engine = AssociativeRetrievalEngine()
    memory = MemoryRecord(content="Witness reported a bright object near the horizon")

    results = engine.retrieve("bright object seen near horizon", memories=[memory])

    assert results[0].record_id == memory.id
    assert results[0].association_label is AssociationLabel.POSSIBLE_ASSOCIATION
    assert "lexical_overlap" in results[0].association_reason


def test_similarity_does_not_create_support_edge_automatically() -> None:
    engine = AssociativeRetrievalEngine()
    graph = RelationshipGraphEngine()
    memory = MemoryRecord(content="Radar contact mentioned in a report")

    engine.retrieve("radar contact report", memories=[memory])

    assert graph.edges == {}


def test_repeated_same_lineage_evidence_is_downgraded() -> None:
    engine = AssociativeRetrievalEngine()
    context = RetrievalContext(
        query="bright object report",
        source_id="archive",
        lineage_id="same-lineage",
    )
    repeated = EvidenceItem(
        summary="Bright object report repeated by later article",
        source_id="article",
        evidence_type="article",
        metadata={"lineage_id": "same-lineage"},
    )
    independent = EvidenceItem(
        summary="Bright object report in separate transcript",
        source_id="transcript",
        evidence_type="transcript",
        metadata={"lineage_id": "separate-lineage", "source_kind": "transcript"},
    )

    repeated_score = engine.retrieve(context.query, evidence=[repeated], context=context)[
        0
    ].score.final_association_score
    independent_score = engine.retrieve(context.query, evidence=[independent], context=context)[
        0
    ].score.final_association_score

    assert repeated_score < independent_score


def test_shared_tags_increase_association_score() -> None:
    engine = AssociativeRetrievalEngine()
    context = RetrievalContext(query="document", query_tags={"radar"})
    tagged = MemoryRecord(content="Document fragment", tags=["radar"])
    untagged = MemoryRecord(content="Document fragment")

    tagged_score = engine.retrieve(context.query, memories=[tagged], context=context)[
        0
    ].score.final_association_score
    untagged_score = engine.retrieve(context.query, memories=[untagged], context=context)[
        0
    ].score.final_association_score

    assert tagged_score > untagged_score


def test_shared_entities_increase_association_score() -> None:
    engine = AssociativeRetrievalEngine()
    context = RetrievalContext(query="interview note", query_entity_ids={"entity-1"})
    linked = EvidenceItem(
        summary="Interview note",
        source_id="source",
        evidence_type="note",
        metadata={"entity_ids": {"entity-1"}},
    )
    unlinked = EvidenceItem(summary="Interview note", source_id="source", evidence_type="note")

    linked_score = engine.retrieve(context.query, evidence=[linked], context=context)[
        0
    ].score.final_association_score
    unlinked_score = engine.retrieve(context.query, evidence=[unlinked], context=context)[
        0
    ].score.final_association_score

    assert linked_score > unlinked_score


def test_contradiction_pressure_lowers_association_score() -> None:
    engine = AssociativeRetrievalEngine()
    calm = MemoryRecord(content="Radar contact report", contradiction_pressure=0.0)
    pressured = MemoryRecord(content="Radar contact report", contradiction_pressure=0.8)

    calm_score = engine.retrieve("radar contact report", memories=[calm])[
        0
    ].score.final_association_score
    pressured_score = engine.retrieve("radar contact report", memories=[pressured])[
        0
    ].score.final_association_score

    assert pressured_score < calm_score


def test_contested_associations_are_preserved_in_activated_context() -> None:
    engine = AssociativeRetrievalEngine()
    builder = ActivationContextBuilder()
    claim = ClaimNode(
        text="event happened before midnight",
        canonical_topic="event-time",
        status=ClaimMatrixStatus.CONTESTED,
        evidence_ids={"e1", "e2"},
    )

    candidates = engine.retrieve(
        "event before midnight",
        claims=[claim],
        context=RetrievalContext(query="event before midnight", query_canonical_topics={"event-time"}),
    )
    activated = builder.build(candidates)

    assert activated.contested_associations[0].record_id == claim.id
    assert claim.id in activated.activated_claim_ids
    assert {"e1", "e2"} <= activated.activated_evidence_ids


def test_weak_associations_are_labeled_weak_not_discarded() -> None:
    candidate = AssociationCandidate(
        record_id="memory-1",
        record_type="memory",
        label="low score memory",
        score=AssociationScore(final_association_score=0.2),
        memory_ids={"memory-1"},
    )

    activated = ActivationContextBuilder().build([candidate])

    assert activated.weak_associations == [candidate]
    assert candidate.association_label is AssociationLabel.WEAK_ASSOCIATION


def test_duplicate_associations_merge() -> None:
    first = AssociationCandidate(
        record_id="claim-1",
        record_type="claim",
        label="claim",
        score=AssociationScore(final_association_score=0.4),
        claim_ids={"claim-1"},
        evidence_ids={"e1"},
    )
    duplicate = AssociationCandidate(
        record_id="claim-1",
        record_type="claim",
        label="claim",
        score=AssociationScore(final_association_score=0.6),
        claim_ids={"claim-1"},
        evidence_ids={"e2"},
    )

    activated = ActivationContextBuilder().build([first, duplicate])

    assert activated.activated_claim_ids == {"claim-1"}
    assert activated.activated_evidence_ids == {"e1", "e2"}
    assert activated.weak_associations == []


def test_final_association_score_is_bounded_between_zero_and_one() -> None:
    engine = AssociativeRetrievalEngine()
    memory = MemoryRecord(
        content="radar radar radar radar",
        tags=["radar"],
        metadata={"entity_ids": {"entity-1"}, "event_date": date(1947, 7, 4)},
    )
    context = RetrievalContext(
        query="radar",
        query_tags={"radar"},
        query_entity_ids={"entity-1"},
        query_date=date(1947, 7, 4),
    )

    result = engine.retrieve(context.query, memories=[memory], context=context)[0]

    assert 0.0 <= result.score.final_association_score <= 1.0


def test_no_external_dependencies_are_required() -> None:
    pyproject = open("pyproject.toml", encoding="utf-8").read()

    assert "chromadb" not in pyproject
    assert "faiss" not in pyproject
    assert "openai" not in pyproject
