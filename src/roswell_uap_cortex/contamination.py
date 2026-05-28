"""Deterministic contamination detection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ContaminationFlag,
    ContaminationFlagType,
    ContaminationReport,
    EvidenceItem,
    EvidenceLineageRecord,
    RawInput,
)


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


@dataclass(slots=True)
class ContaminationDetector:
    """Rule-based contamination and source-quality flagging for ingestion."""

    seen_source_uris: set[str] | None = None
    speculative_terms: tuple[str, ...] = (
        "maybe",
        "perhaps",
        "rumor",
        "rumour",
        "allegedly",
        "speculative",
        "unverified",
        "i think",
        "could be",
        "might be",
    )
    fictional_terms: tuple[str, ...] = (
        "astrophage",
        "petrova line",
        "warp drive",
        "lightsaber",
        "federation starship",
    )

    def __post_init__(self) -> None:
        if self.seen_source_uris is None:
            self.seen_source_uris = set()

    def detect(
        self,
        raw_input: RawInput,
        evidence: EvidenceItem | None = None,
        *,
        duplicate_source_uri: bool = False,
        derivative_source: bool = False,
    ) -> list[ContaminationFlag]:
        text = raw_input.raw_text.casefold()
        flags: list[ContaminationFlag] = []
        evidence_id = evidence.id if evidence else None

        def add(flag_type: ContaminationFlagType, note: str) -> None:
            flags.append(
                ContaminationFlag(
                    flag_type=flag_type,
                    input_id=raw_input.input_id,
                    evidence_id=evidence_id,
                    source_uri=raw_input.source_uri,
                    note=note,
                )
            )

        if raw_input.collected_at is None and not raw_input.declared_event_hint:
            add(ContaminationFlagType.MISSING_DATE, "no collected_at or declared event hint")
        if not raw_input.source_uri:
            add(ContaminationFlagType.MISSING_SOURCE_URI, "source_uri is missing")
        if not raw_input.title:
            add(ContaminationFlagType.MISSING_TITLE, "title is missing")
        if derivative_source:
            add(ContaminationFlagType.DERIVATIVE_SOURCE, "metadata indicates derivative source")
        if duplicate_source_uri:
            add(ContaminationFlagType.REPEATED_SOURCE_URI, "source_uri was already ingested")
        if self._is_anonymous(raw_input):
            add(ContaminationFlagType.ANONYMOUS_SOURCE, "source appears anonymous or unattributed")
        if any(term in text for term in self.speculative_terms):
            add(ContaminationFlagType.SPECULATIVE_LANGUAGE, "speculative language detected")
        if any(term in text for term in self.fictional_terms):
            add(
                ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS,
                "fictional contamination term detected",
            )
        if self._weak_chain_of_custody(raw_input):
            add(ContaminationFlagType.WEAK_CHAIN_OF_CUSTODY, "weak chain-of-custody metadata")

        if raw_input.source_uri:
            self.seen_source_uris.add(raw_input.source_uri)
        return self._dedupe(flags)

    def _is_anonymous(self, raw_input: RawInput) -> bool:
        author = str(raw_input.metadata.get("author", "")).casefold()
        return author in {"anonymous", "unknown"} or raw_input.source_kind == "anonymous"

    def _weak_chain_of_custody(self, raw_input: RawInput) -> bool:
        if raw_input.metadata.get("chain_of_custody") in {"weak", "unclear", "unknown"}:
            return True
        return raw_input.source_kind in {"forum", "repost", "social_media", "unknown"}

    def _dedupe(self, flags: list[ContaminationFlag]) -> list[ContaminationFlag]:
        deduped: dict[ContaminationFlagType, ContaminationFlag] = {}
        for flag in flags:
            deduped.setdefault(flag.flag_type, flag)
        return list(deduped.values())
