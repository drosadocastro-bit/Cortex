"""Semantic guardrails for loaded persistence snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import PersistenceEnvelope


@dataclass(slots=True)
class PersistenceGuardrailResult:
    """Guardrail warnings and errors for loaded snapshots."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PersistenceGuardrails:
    """Validate persistence boundaries without applying snapshot records."""

    def check(self, envelope: PersistenceEnvelope) -> PersistenceGuardrailResult:
        result = PersistenceGuardrailResult()

        for record in envelope.records.get("memory_records", []):
            if record.payload.get("archival") is True:
                result.warnings.append(f"archived memory preserved: {record.record_id}")
            if float(record.payload.get("contradiction_pressure", 0.0) or 0.0) > 0:
                result.warnings.append(f"contradiction pressure preserved: {record.record_id}")

        if envelope.records.get("discourse_responses"):
            result.warnings.append("loaded discourse remains discourse, not truth")

        evidence_ids = {
            record.record_id
            for record in envelope.records.get("evidence_items", [])
            if record.record_id is not None
        }
        provenance_ids = {
            record.payload.get("evidence_id")
            for record in envelope.records.get("provenance_records", [])
        }
        if evidence_ids - provenance_ids:
            result.warnings.append("provenance must remain attached to evidence")

        if envelope.records.get("claims") and not envelope.records.get("evidence_items"):
            result.warnings.append("loaded snapshot contains claims without evidence payload")

        return result
