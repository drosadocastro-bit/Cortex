from pathlib import Path
import re
import tomllib

from roswell_uap_cortex import (
    EvidenceItem,
    PersistenceEnvelope,
    PersistenceManifest,
    PersistenceRecord,
    PersistenceStore,
    SCHEMA_VERSION,
    SnapshotMetadata,
    utc_now,
)


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "roswell_uap_cortex"


def test_project_dependency_surface_stays_intentionally_small() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = set(pyproject["project"].get("dependencies", []))

    assert dependencies == {"networkx>=3.0", "python-dateutil>=2.8"}
    assert "openai" not in "\n".join(dependencies).casefold()
    assert "sentence-transformers" not in "\n".join(dependencies).casefold()
    assert "chromadb" not in "\n".join(dependencies).casefold()


def test_core_source_avoids_network_process_and_dynamic_execution_patterns() -> None:
    forbidden = re.compile(
        r"import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system",
        re.IGNORECASE,
    )
    matches: list[str] = []
    for path in sorted(SRC.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if forbidden.search(text):
            matches.append(path.name)

    assert matches == []


def test_docs_do_not_contain_known_mojibake_markers() -> None:
    paths = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    mojibake = re.compile("\u00e2|\ufffd")
    offenders = [
        str(path.relative_to(ROOT))
        for path in paths
        if mojibake.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


def test_public_api_smoke_imports_foundational_symbols() -> None:
    item = EvidenceItem(summary="synthetic", source_id="source", evidence_type="note")

    assert item.summary == "synthetic"
    assert PersistenceStore().schema_version


def test_persistence_load_preserves_unknown_payload_without_execution() -> None:
    envelope = PersistenceEnvelope(
        manifest=PersistenceManifest(
            metadata=SnapshotMetadata(
                snapshot_id="hygiene",
                created_at=utc_now(),
                schema_version=SCHEMA_VERSION,
                record_counts={"unknown_records": 1},
            )
        ),
        records={
            "unknown_records": [
                PersistenceRecord(
                    record_type="UnknownRecord",
                    payload={"code": "__import__('os').system('echo unsafe')"},
                    record_id="unknown-1",
                )
            ]
        },
    )
    temp_dir = ROOT / "tests" / ".tmp_hygiene"
    temp_dir.mkdir(exist_ok=True)
    path = temp_dir / "snapshot_noexec.json"
    store = PersistenceStore(atomic_writes=False)
    store.save(envelope, path)

    result = store.load(path)

    assert result.success
    assert result.envelope is not None
    loaded = result.envelope.records["unknown_records"][0]
    assert loaded.payload["code"] == "__import__('os').system('echo unsafe')"
