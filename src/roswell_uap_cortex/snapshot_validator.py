"""Validation for persistence snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import PersistenceEnvelope
from roswell_uap_cortex.snapshot import SCHEMA_VERSION, SnapshotBuilder


@dataclass(slots=True)
class SnapshotValidationResult:
    """Validation warnings and errors for a snapshot."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class SnapshotValidator:
    """Validate required fields, counts, schema, checksum, and provenance signals."""

    expected_schema_version: str = SCHEMA_VERSION
    builder: SnapshotBuilder = field(default_factory=SnapshotBuilder)

    def validate(self, envelope: PersistenceEnvelope) -> SnapshotValidationResult:
        result = SnapshotValidationResult()
        metadata = envelope.manifest.metadata

        if envelope.manifest.saved_by != "roswell_uap_cortex":
            result.warnings.append("unknown snapshot producer")
        if envelope.manifest.format != "json_snapshot":
            result.errors.append("unsupported snapshot format")
        if metadata.schema_version != self.expected_schema_version:
            result.errors.append(f"incompatible schema version: {metadata.schema_version}")

        for key, expected_count in metadata.record_counts.items():
            actual_count = len(envelope.records.get(key, []))
            if actual_count != expected_count:
                result.errors.append(
                    f"record count mismatch for {key}: expected {expected_count}, found {actual_count}"
                )

        if metadata.checksum and not result.errors:
            actual_checksum = self.builder.checksum(envelope)
            if actual_checksum != metadata.checksum:
                result.errors.append("snapshot checksum mismatch")

        evidence_ids = {
            record.record_id
            for record in envelope.records.get("evidence_items", [])
            if record.record_id is not None
        }
        provenance_ids = {
            record.payload.get("evidence_id")
            for record in envelope.records.get("provenance_records", [])
        }
        lineage_ids = {
            record.payload.get("evidence_id")
            for record in envelope.records.get("lineage_records", [])
        }
        missing_provenance = sorted(evidence_ids - provenance_ids)
        missing_lineage = sorted(evidence_ids - lineage_ids)
        if missing_provenance:
            result.warnings.append(f"missing provenance for evidence: {', '.join(missing_provenance)}")
        if missing_lineage:
            result.warnings.append(f"missing lineage for evidence: {', '.join(missing_lineage)}")

        return result
