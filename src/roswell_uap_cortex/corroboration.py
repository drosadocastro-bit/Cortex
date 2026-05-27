"""Corroboration assessment for repeated versus independent evidence."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from roswell_uap_cortex.models import CorroborationAssessment, EvidenceLineageRecord


@dataclass(slots=True)
class CorroborationLayer:
    """Separate independent corroboration from same-source repetition."""

    def assess(
        self,
        records: list[EvidenceLineageRecord],
        *,
        claim_key: str,
    ) -> CorroborationAssessment:
        claim_records = [record for record in records if record.claim_key == claim_key]
        by_origin: dict[str, list[EvidenceLineageRecord]] = defaultdict(list)

        for record in claim_records:
            origin = record.original_source_id or record.source_id
            by_origin[origin].append(record)

        independent_source_ids = sorted(by_origin)
        repeated_source_ids = sorted(
            record.source_id
            for grouped in by_origin.values()
            if len(grouped) > 1
            for record in grouped[1:]
        )

        independent_count = len(independent_source_ids)
        repeated_count = len(claim_records) - independent_count
        score = 0.0 if not claim_records else independent_count / len(claim_records)

        return CorroborationAssessment(
            claim_key=claim_key,
            independent_source_ids=independent_source_ids,
            repeated_source_ids=repeated_source_ids,
            independent_count=independent_count,
            repeated_count=repeated_count,
            corroboration_score=score,
        )
