"""Local deterministic persistence for review sessions and audit trails."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.models import (
    PersistenceManifest,
    PersistenceRecord,
    ReviewSession,
    SessionAuditTrail,
    SessionLoadResult,
    SessionPersistenceEnvelope,
    SessionSaveResult,
    SnapshotMetadata,
)
from roswell_uap_cortex.serialization import Serializer


SESSION_SCHEMA_VERSION = "phase-21-session-v1"


@dataclass(slots=True)
class SessionPersistenceStore:
    """Save and load review-session state without applying it to truth records."""

    schema_version: str = SESSION_SCHEMA_VERSION
    atomic_writes: bool = False
    serializer: Serializer = field(default_factory=Serializer)

    def build_envelope(
        self,
        sessions: list[ReviewSession],
        audit_trails: list[SessionAuditTrail],
        *,
        notes: list[str] | None = None,
    ) -> SessionPersistenceEnvelope:
        records = {
            "sessions": [self.serializer.serialize_record(session) for session in sessions],
            "audit_trails": [self.serializer.serialize_record(trail) for trail in audit_trails],
        }
        record_counts = {key: len(value) for key, value in records.items()}
        snapshot_id = str(uuid5(NAMESPACE_URL, json.dumps(self.serializer.to_json_compatible(records), sort_keys=True, ensure_ascii=True)))
        manifest = PersistenceManifest(
            metadata=SnapshotMetadata(
                snapshot_id=snapshot_id,
                created_at=datetime.fromisoformat("1970-01-01T00:00:00+00:00"),
                schema_version=self.schema_version,
                record_counts=record_counts,
                notes=notes or ["session persistence envelope; annotations are not truth state"],
            ),
            format="json_session_snapshot",
        )
        envelope = SessionPersistenceEnvelope(manifest=manifest, sessions=sessions, audit_trails=audit_trails, records=records)
        envelope.manifest.metadata.checksum = self.checksum(envelope)
        return envelope

    def save(self, envelope: SessionPersistenceEnvelope, path: str | Path) -> SessionSaveResult:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        envelope.manifest.metadata.checksum = self.checksum(envelope)
        payload = self.serializer.to_json_compatible(envelope)
        encoded = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True)
        if self.atomic_writes:
            tmp_path = target.with_name(f"{target.name}.tmp")
            tmp_path.write_text(encoded, encoding="utf-8")
            tmp_path.replace(target)
        else:
            target.write_text(encoded, encoding="utf-8")
        return SessionSaveResult(path=str(target), envelope=envelope, checksum=envelope.manifest.metadata.checksum)

    def load(self, path: str | Path) -> SessionLoadResult:
        target = Path(path)
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
            envelope = self._envelope_from_payload(payload)
        except Exception as exc:
            return SessionLoadResult(path=str(target), errors=[str(exc)], success=False)

        errors, warnings = self.validate(envelope)
        return SessionLoadResult(
            path=str(target),
            envelope=None if errors else envelope,
            errors=errors,
            warnings=warnings,
            success=not errors,
        )

    def validate(self, envelope: SessionPersistenceEnvelope) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        metadata = envelope.manifest.metadata
        if envelope.manifest.format != "json_session_snapshot":
            errors.append("unsupported session snapshot format")
        if metadata.schema_version != self.schema_version:
            errors.append(f"incompatible session schema version: {metadata.schema_version}")
        for key, expected in metadata.record_counts.items():
            actual = len(envelope.records.get(key, []))
            if actual != expected:
                errors.append(f"session record count mismatch for {key}: expected {expected}, found {actual}")
        if metadata.checksum and not errors and self.checksum(envelope) != metadata.checksum:
            errors.append("session checksum mismatch")
        warnings.append("loaded session annotations are not evidence, claim confirmation, source rejection, or graph mutation")
        return errors, warnings

    def checksum(self, envelope: SessionPersistenceEnvelope) -> str:
        payload = self.serializer.to_json_compatible(envelope)
        payload["manifest"]["metadata"]["checksum"] = ""
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _envelope_from_payload(self, payload: dict) -> SessionPersistenceEnvelope:
        metadata_payload = payload["manifest"]["metadata"]
        metadata = SnapshotMetadata(
            snapshot_id=metadata_payload["snapshot_id"],
            created_at=self.serializer._restore_value(metadata_payload["created_at"], datetime),
            schema_version=metadata_payload["schema_version"],
            record_counts=dict(metadata_payload.get("record_counts", {})),
            checksum=metadata_payload.get("checksum", ""),
            notes=list(metadata_payload.get("notes", [])),
        )
        manifest = PersistenceManifest(
            metadata=metadata,
            saved_by=payload["manifest"].get("saved_by", "roswell_uap_cortex"),
            format=payload["manifest"].get("format", "json_session_snapshot"),
        )
        records = {
            group: [
                PersistenceRecord(
                    record_type=record["record_type"],
                    payload=dict(record.get("payload", {})),
                    record_id=record.get("record_id"),
                    unknown_fields=dict(record.get("unknown_fields", {})),
                )
                for record in values
            ]
            for group, values in payload.get("records", {}).items()
        }
        sessions = [self.serializer.deserialize_record(record) for record in records.get("sessions", [])]
        audit_trails = [self.serializer.deserialize_record(record) for record in records.get("audit_trails", [])]
        return SessionPersistenceEnvelope(manifest=manifest, sessions=sessions, audit_trails=audit_trails, records=records)
