"""Deterministic citation formatting for investigative discourse."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import DiscourseCitation, ProvenanceRecord, SourceLineageRecord


@dataclass(slots=True)
class CitationFormatter:
    """Create and format provenance-backed citations."""

    def citation_for(
        self,
        evidence_id: str,
        *,
        provenance: ProvenanceRecord | None = None,
        lineage: SourceLineageRecord | None = None,
        source_id: str | None = None,
    ) -> DiscourseCitation:
        citation = DiscourseCitation(
            evidence_id=evidence_id,
            source_id=source_id or (lineage.source_id if lineage else None),
            lineage_id=lineage.lineage_id if lineage else None,
            provenance_id=provenance.id if provenance else None,
            page_number=provenance.page_number if provenance else None,
            timestamp_range=provenance.timestamp_range if provenance else None,
        )
        citation.label = self.format(citation)
        return citation

    def format(self, citation: DiscourseCitation) -> str:
        parts: list[str] = []
        if citation.evidence_id:
            parts.append(f"evidence:{citation.evidence_id}")
        if citation.source_id:
            parts.append(f"source:{citation.source_id}")
        if citation.lineage_id:
            parts.append(f"lineage:{citation.lineage_id}")
        if citation.provenance_id:
            parts.append(f"provenance:{citation.provenance_id}")
        if citation.page_number is not None:
            parts.append(f"page:{citation.page_number}")
        if citation.timestamp_range is not None:
            parts.append(f"time:{citation.timestamp_range[0]}-{citation.timestamp_range[1]}")
        return " | ".join(parts) if parts else "uncited"

    def merge(self, citations: list[DiscourseCitation]) -> list[DiscourseCitation]:
        merged: dict[tuple[str | None, str | None, str | None], DiscourseCitation] = {}
        for citation in citations:
            key = (citation.evidence_id, citation.provenance_id, citation.lineage_id)
            if key not in merged:
                if not citation.label:
                    citation.label = self.format(citation)
                merged[key] = citation
        return [merged[key] for key in sorted(merged, key=lambda item: tuple(str(part) for part in item))]
