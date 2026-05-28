"""Mandatory provenance extraction for ingested evidence."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import EvidenceItem, ProvenanceRecord, RawInput


@dataclass(slots=True)
class ProvenanceExtractor:
    """Create non-empty provenance records for every ingested evidence item."""

    ingestion_method: str = "deterministic_raw_input_normalization"
    extraction_method: str = "deterministic_sentence_split"

    def extract(
        self,
        raw_input: RawInput,
        evidence: EvidenceItem,
        *,
        extracted_span: tuple[int, int] | None = None,
    ) -> ProvenanceRecord:
        source_uri = raw_input.source_uri or f"unknown:{raw_input.input_id}"
        source_kind = raw_input.source_kind or "unknown"
        metadata = {
            "title": raw_input.title,
            "declared_event_hint": raw_input.declared_event_hint,
        }
        page_number = raw_input.metadata.get("page_number")
        timestamp_range = raw_input.metadata.get("timestamp_range")

        return ProvenanceRecord(
            evidence_id=evidence.id,
            source_uri=source_uri,
            source_kind=source_kind,
            ingestion_method=self.ingestion_method,
            extraction_method=self.extraction_method,
            original_input_id=raw_input.input_id,
            extracted_span=extracted_span,
            page_number=page_number,
            timestamp_range=timestamp_range,
            metadata=metadata,
        )
