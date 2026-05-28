"""Local JSON snapshot persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from roswell_uap_cortex.models import (
    LoadResult,
    PersistenceEnvelope,
    PersistenceManifest,
    PersistenceRecord,
    SaveResult,
    SnapshotMetadata,
)
from roswell_uap_cortex.persistence_guardrails import PersistenceGuardrails
from roswell_uap_cortex.serialization import Serializer
from roswell_uap_cortex.snapshot import SCHEMA_VERSION, SnapshotBuilder
from roswell_uap_cortex.snapshot_validator import SnapshotValidator


@dataclass(slots=True)
class PersistenceStore:
    """Save and load immutable local JSON snapshots."""

    schema_version: str = SCHEMA_VERSION
    atomic_writes: bool = False
    serializer: Serializer = field(default_factory=Serializer)
    builder: SnapshotBuilder = field(default_factory=SnapshotBuilder)
    validator: SnapshotValidator = field(default_factory=SnapshotValidator)
    guardrails: PersistenceGuardrails = field(default_factory=PersistenceGuardrails)

    def save(self, envelope: PersistenceEnvelope, path: str | Path) -> SaveResult:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        envelope.manifest.metadata.checksum = self.builder.checksum(envelope)
        payload = self.serializer.to_json_compatible(envelope)
        encoded = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True)
        if self.atomic_writes:
            tmp_path = target.with_name(f"{target.name}.tmp")
            tmp_path.write_text(encoded, encoding="utf-8")
            tmp_path.replace(target)
        else:
            target.write_text(encoded, encoding="utf-8")
        return SaveResult(
            path=str(target),
            envelope=envelope,
            checksum=envelope.manifest.metadata.checksum,
        )

    def load(self, path: str | Path) -> LoadResult:
        target = Path(path)
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
            envelope = self._envelope_from_payload(payload)
        except Exception as exc:
            return LoadResult(path=str(target), envelope=None, errors=[str(exc)], success=False)

        validation = self.validator.validate(envelope)
        guardrail_result = self.guardrails.check(envelope)
        errors = validation.errors + guardrail_result.errors
        warnings = validation.warnings + guardrail_result.warnings
        return LoadResult(
            path=str(target),
            envelope=None if errors else envelope,
            warnings=warnings,
            errors=errors,
            success=not errors,
        )

    def _envelope_from_payload(self, payload: dict) -> PersistenceEnvelope:
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
            saved_by=payload["manifest"].get("saved_by", "unknown"),
            format=payload["manifest"].get("format", "unknown"),
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
        return PersistenceEnvelope(manifest=manifest, records=records)
