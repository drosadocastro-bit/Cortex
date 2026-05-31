import json
from pathlib import Path

from roswell_uap_cortex import (
    GraphNode,
    GraphNodeType,
    RelationshipGraphEngine,
    ReviewDecisionType,
    ReviewSessionEngine,
    SessionAuditFormatter,
    SessionAuditLogger,
    SessionAuditRecord,
    SessionPersistenceStore,
    SessionSaveResult,
    WorkingMemoryEngine,
)


LOCAL_TMP = Path("tests/.tmp_session_persistence")


def local_path(name: str) -> Path:
    LOCAL_TMP.mkdir(exist_ok=True)
    return LOCAL_TMP / name


def sample_session_and_trail():
    state = WorkingMemoryEngine().build_state(query="session persistence")
    engine = ReviewSessionEngine()
    session = engine.start_session("Session Persistence", state)
    delta = engine.record_decision(
        session,
        item_id="claim-1",
        item_type="claim",
        decision_type=ReviewDecisionType.DEFERRED,
        notes=["needs provenance"],
    )
    logger = SessionAuditLogger()
    trail = logger.build_trail(
        session,
        [
            logger.start(session),
            logger.decision(session, session.decisions[-1]),
            logger.report(session),
        ],
    )
    return session, trail, delta


def test_session_saves_and_loads_deterministically() -> None:
    session, trail, _ = sample_session_and_trail()
    store = SessionPersistenceStore()
    envelope = store.build_envelope([session], [trail])
    path = local_path("session_save_load.json")

    save_result = store.save(envelope, path)
    load_result = store.load(path)

    assert isinstance(save_result, SessionSaveResult)
    assert load_result.success
    assert load_result.envelope is not None
    assert load_result.envelope.manifest.metadata.checksum == envelope.manifest.metadata.checksum


def test_audit_records_preserve_event_order() -> None:
    _, trail, _ = sample_session_and_trail()

    assert [record.event_type for record in trail.records] == [
        "decision:deferred",
        "session_report",
        "session_started",
    ]


def test_decisions_deferred_and_unresolved_round_trip() -> None:
    session, trail, _ = sample_session_and_trail()
    path = local_path("session_decisions.json")
    store = SessionPersistenceStore()
    store.save(store.build_envelope([session], [trail]), path)

    loaded_session = store.load(path).envelope.sessions[0]

    assert loaded_session.decisions[0].decision_type is ReviewDecisionType.DEFERRED
    assert loaded_session.state.deferred_items[0].item_id == "claim-1"
    assert "claim-1" in loaded_session.state.unresolved_item_ids


def test_audit_trail_does_not_mutate_session_truth_state() -> None:
    session, trail, _ = sample_session_and_trail()
    before = set(session.state.unresolved_item_ids)

    SessionAuditLogger().build_trail(session, list(trail.records))

    assert session.state.unresolved_item_ids == before


def test_corrupted_checksum_is_detected() -> None:
    session, trail, _ = sample_session_and_trail()
    store = SessionPersistenceStore()
    envelope = store.build_envelope([session], [trail])
    envelope.manifest.metadata.checksum = "bad"

    errors, _ = store.validate(envelope)

    assert "session checksum mismatch" in errors


def test_incompatible_session_schema_is_rejected() -> None:
    session, trail, _ = sample_session_and_trail()
    store = SessionPersistenceStore()
    envelope = store.build_envelope([session], [trail])
    envelope.manifest.metadata.schema_version = "future-session-v999"

    errors, _ = store.validate(envelope)

    assert errors == ["incompatible session schema version: future-session-v999"]


def test_unknown_fields_are_preserved_in_session_records() -> None:
    record = SessionAuditRecord(
        event_type="custom",
        session_id="session-1",
        metadata={"unknown_fields": {"future": "preserved"}},
    )

    assert record.metadata["unknown_fields"] == {"future": "preserved"}


def test_formatter_includes_limitations() -> None:
    session, trail, _ = sample_session_and_trail()
    text = SessionAuditFormatter().format(session, trail)

    assert "Limitations" in text
    assert "not evidence, claim confirmation, source rejection, or graph mutation" in text


def test_load_never_creates_graph_edges_or_records() -> None:
    session, trail, _ = sample_session_and_trail()
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))
    path = local_path("session_no_apply.json")
    store = SessionPersistenceStore()

    store.save(store.build_envelope([session], [trail]), path)
    loaded = store.load(path)

    assert loaded.success
    assert graph.edges == {}
    assert loaded.envelope.sessions[0].state.deferred_items[0].item_id == "claim-1"


def test_save_uses_deterministic_json_output() -> None:
    session, trail, _ = sample_session_and_trail()
    store = SessionPersistenceStore()
    envelope = store.build_envelope([session], [trail])
    first_path = local_path("session_first.json")
    second_path = local_path("session_second.json")

    store.save(envelope, first_path)
    store.save(envelope, second_path)

    assert json.loads(first_path.read_text(encoding="utf-8")) == json.loads(second_path.read_text(encoding="utf-8"))
