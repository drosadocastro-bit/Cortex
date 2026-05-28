"""Build immutable persistence snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from roswell_uap_cortex.models import (
    ActivatedContext,
    Claim,
    ClaimNode,
    Contradiction,
    DiscourseResponse,
    EntityNode,
    EvidenceItem,
    EventNode,
    GraphNode,
    MemoryRecord,
    PersistenceEnvelope,
    PersistenceManifest,
    ProvenanceRecord,
    ReasoningOutput,
    RelationshipEdge,
    SnapshotMetadata,
    SourceLineageRecord,
    SourceNode,
    SourceTrust,
)
from roswell_uap_cortex.serialization import Serializer


SCHEMA_VERSION = "phase-8-v1"


@dataclass(slots=True)
class SnapshotBuilder:
    """Build deterministic snapshot envelopes from structured records."""

    serializer: Serializer = field(default_factory=Serializer)

    def build(
        self,
        *,
        evidence_items: list[EvidenceItem] | None = None,
        claims: list[Claim] | None = None,
        source_trusts: list[SourceTrust] | None = None,
        memory_records: list[MemoryRecord] | None = None,
        graph_nodes: list[GraphNode | EntityNode | EventNode | ClaimNode | SourceNode] | None = None,
        relationship_edges: list[RelationshipEdge] | None = None,
        contradictions: list[Contradiction] | None = None,
        provenance_records: list[ProvenanceRecord] | None = None,
        lineage_records: list[SourceLineageRecord] | None = None,
        activated_contexts: list[ActivatedContext] | None = None,
        reasoning_outputs: list[ReasoningOutput] | None = None,
        discourse_responses: list[DiscourseResponse] | None = None,
        notes: list[str] | None = None,
        created_at: datetime | None = None,
        schema_version: str = SCHEMA_VERSION,
    ) -> PersistenceEnvelope:
        records = {
            "evidence_items": self._records(evidence_items or []),
            "claims": self._records(claims or []),
            "source_trusts": self._records(source_trusts or []),
            "memory_records": self._records(memory_records or []),
            "graph_nodes": self._records(graph_nodes or []),
            "relationship_edges": self._records(relationship_edges or []),
            "contradictions": self._records(contradictions or []),
            "provenance_records": self._records(provenance_records or []),
            "lineage_records": self._records(lineage_records or []),
            "activated_contexts": self._records(activated_contexts or []),
            "reasoning_outputs": self._records(reasoning_outputs or []),
            "discourse_responses": self._records(discourse_responses or []),
        }
        record_counts = {key: len(value) for key, value in records.items()}
        content_hash = self._hash({"records": self.serializer.to_json_compatible(records)})
        metadata = SnapshotMetadata(
            snapshot_id=f"snapshot:{content_hash}",
            created_at=created_at or datetime(1970, 1, 1, tzinfo=timezone.utc),
            schema_version=schema_version,
            record_counts=record_counts,
            checksum="",
            notes=notes or [],
        )
        envelope = PersistenceEnvelope(
            manifest=PersistenceManifest(metadata=metadata),
            records=records,
        )
        envelope.manifest.metadata.checksum = self.checksum(envelope)
        return envelope

    def checksum(self, envelope: PersistenceEnvelope) -> str:
        payload = self.serializer.to_json_compatible(envelope)
        payload["manifest"]["metadata"]["checksum"] = ""
        return self._hash(payload)

    def _records(self, values: list[Any]) -> list:
        return [
            self.serializer.serialize_record(value)
            for value in sorted(values, key=lambda item: self._record_sort_key(item))
        ]

    def _record_sort_key(self, value: Any) -> str:
        return str(
            getattr(value, "id", None)
            or getattr(value, "source_id", None)
            or getattr(value, "evidence_id", None)
            or repr(value)
        )

    def _hash(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
