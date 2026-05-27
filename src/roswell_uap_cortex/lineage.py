"""Evidence lineage tracking for copied and retold sources."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import EvidenceLineageRecord


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
