"""Deterministic contamination detection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from roswell_uap_cortex.models import ContaminationReport, EvidenceLineageRecord


@dataclass(slots=True)
class ContaminationEngine:
    """Flag copy chains, loops, ambiguity, and speculative escalation."""

    speculative_kinds: tuple[str, ...] = ("speculation", "forum", "youtube", "tiktok")

    def assess_lineage(
        self,
        records: list[EvidenceLineageRecord],
    ) -> list[ContaminationReport]:
        by_source = {record.source_id: record for record in records}
        by_claim_and_origin: dict[tuple[str, str | None], list[EvidenceLineageRecord]] = defaultdict(list)
        reports: list[ContaminationReport] = []

        for record in records:
            by_claim_and_origin[(record.claim_key, record.original_source_id)].append(record)

        for record in records:
            flags = list(record.contamination_flags)
            same_origin = by_claim_and_origin[(record.claim_key, record.original_source_id)]

            if len(same_origin) > 1:
                flags.append("copy-chain contamination")
            if record.parent_source_id and record.parent_source_id == record.source_id:
                flags.append("citation loop")
            if record.parent_source_id and self._has_loop(record, by_source):
                flags.append("citation loop")
            if any(item in record.transformations for item in ("fictionalized", "dramatized")):
                flags.append("fictional contamination")
            if record.source_kind in self.speculative_kinds or "speculative" in record.transformations:
                flags.append("speculative escalation")
            if record.original_source_id is None or record.source_kind == "unknown":
                flags.append("source ambiguity")
            if len(same_origin) > 1 and record.parent_source_id:
                flags.append("semantic duplication")

            deduped = sorted(set(flags))
            reports.append(
                ContaminationReport(
                    record_id=record.id,
                    flags=deduped,
                    risk_score=min(1.0, len(deduped) * 0.18),
                )
            )

        return reports

    def _has_loop(
        self,
        record: EvidenceLineageRecord,
        by_source: dict[str, EvidenceLineageRecord],
    ) -> bool:
        seen = {record.source_id}
        parent_id = record.parent_source_id
        while parent_id:
            if parent_id in seen:
                return True
            seen.add(parent_id)
            parent = by_source.get(parent_id)
            if parent is None:
                return False
            parent_id = parent.parent_source_id
        return False
