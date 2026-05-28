"""Evidence lineage tracking for copied and retold sources."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.models import (
    EvidenceItem,
    EvidenceLineageRecord,
    LineageType,
    RawInput,
    SourceLineageRecord,
)


@dataclass(slots=True)
class EvidenceLineageEngine:
    """Trace source ancestry so repeated copies are not treated as independent."""

    def index_by_source(
        self,
        records: list[EvidenceLineageRecord],
    ) -> dict[str, EvidenceLineageRecord]:
        return {record.source_id: record for record in records}

    def original_source_for(
        self,
        record: EvidenceLineageRecord,
        records_by_source: dict[str, EvidenceLineageRecord],
    ) -> str:
        seen: set[str] = set()
        current = record
        while current.parent_source_id and current.parent_source_id not in seen:
            seen.add(current.source_id)
            parent = records_by_source.get(current.parent_source_id)
            if parent is None:
                break
            current = parent
        return current.original_source_id or current.source_id

    def copy_chain_for(
        self,
        record: EvidenceLineageRecord,
        records_by_source: dict[str, EvidenceLineageRecord],
    ) -> list[str]:
        chain = [record.source_id]
        seen = {record.source_id}
        current = record
        while current.parent_source_id and current.parent_source_id not in seen:
            chain.append(current.parent_source_id)
            seen.add(current.parent_source_id)
            parent = records_by_source.get(current.parent_source_id)
            if parent is None:
                break
            current = parent
        return chain

    def share_original_source(
        self,
        first: EvidenceLineageRecord,
        second: EvidenceLineageRecord,
        records_by_source: dict[str, EvidenceLineageRecord],
    ) -> bool:
        return self.original_source_for(first, records_by_source) == self.original_source_for(
            second,
            records_by_source,
        )


@dataclass(slots=True)
class LineageTracker:
    """Assign ingestion lineage so repeated and derivative sources remain visible."""

    source_uri_to_lineage: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.source_uri_to_lineage is None:
            self.source_uri_to_lineage = {}

    def track(self, raw_input: RawInput, evidence: EvidenceItem) -> SourceLineageRecord:
        source_uri = raw_input.source_uri
        parent_source_id = raw_input.metadata.get("parent_source_id")
        derived_from = raw_input.metadata.get("derived_from")
        duplicate_source_uri = bool(source_uri and source_uri in self.source_uri_to_lineage)

        if parent_source_id or derived_from:
            lineage_type = LineageType.DERIVATIVE_SOURCE
            lineage_anchor = str(parent_source_id or derived_from)
        elif duplicate_source_uri and source_uri:
            lineage_type = self._lineage_type_for_source_kind(raw_input.source_kind)
            lineage_anchor = source_uri
        else:
            lineage_type = self._lineage_type_for_source_kind(raw_input.source_kind)
            lineage_anchor = source_uri or raw_input.input_id

        if duplicate_source_uri and source_uri:
            lineage_id = self.source_uri_to_lineage[source_uri]
        elif lineage_type is LineageType.DERIVATIVE_SOURCE:
            lineage_id = str(uuid5(NAMESPACE_URL, f"lineage:{lineage_anchor}"))
        else:
            lineage_id = str(uuid5(NAMESPACE_URL, f"lineage:{lineage_anchor}"))

        if source_uri and source_uri not in self.source_uri_to_lineage:
            self.source_uri_to_lineage[source_uri] = lineage_id

        notes: list[str] = []
        if duplicate_source_uri:
            notes.append("duplicate source_uri shares existing lineage")
        if lineage_type is LineageType.DERIVATIVE_SOURCE:
            notes.append("derivative metadata links this input to a parent source")

        evidence.metadata["lineage_id"] = lineage_id
        evidence.metadata["lineage_type"] = lineage_type.value
        evidence.metadata["parent_source_id"] = parent_source_id
        evidence.metadata["derived_from"] = derived_from

        return SourceLineageRecord(
            evidence_id=evidence.id,
            source_id=evidence.source_id,
            lineage_id=lineage_id,
            lineage_type=lineage_type,
            source_uri=source_uri,
            parent_source_id=parent_source_id,
            derived_from=derived_from,
            duplicate_source_uri=duplicate_source_uri,
            notes=notes,
        )

    def _lineage_type_for_source_kind(self, source_kind: str) -> LineageType:
        normalized = source_kind.casefold()
        if normalized in {"official_record", "archival_document", "transcript", "primary"}:
            return LineageType.PRIMARY_SOURCE
        if normalized in {"note", "news", "book", "secondary"}:
            return LineageType.SECONDARY_SOURCE
        return LineageType.UNKNOWN_LINEAGE
