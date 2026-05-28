"""Deterministic evidence ingestion and normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.contamination import ContaminationDetector
from roswell_uap_cortex.lineage import LineageTracker
from roswell_uap_cortex.models import (
    ContaminationFlag,
    ContaminationFlagType,
    EvidenceCategory,
    EvidenceItem,
    ExtractedObservation,
    IngestionResult,
    LineageType,
    RawInput,
)
from roswell_uap_cortex.provenance import ProvenanceExtractor


@dataclass(slots=True)
class IngestionNormalizer:
    """Convert raw inputs into evidence records with provenance and lineage."""

    provenance_extractor: ProvenanceExtractor = field(default_factory=ProvenanceExtractor)
    lineage_tracker: LineageTracker = field(default_factory=LineageTracker)
    contamination_detector: ContaminationDetector = field(default_factory=ContaminationDetector)

    def ingest(self, raw_input: RawInput) -> IngestionResult:
        observations = self._extract_observations(raw_input)
        result = IngestionResult(
            raw_input_id=raw_input.input_id,
            source_trust_hints=dict(raw_input.metadata.get("source_trust_hints", {})),
            ingestion_notes=["deterministic ingestion; no claim confirmation created"],
        )
        result.observations.extend(observations)
        result.ingestion_warnings.extend(self._quality_warnings(raw_input))

        if not observations:
            observations = [
                ExtractedObservation(
                    input_id=raw_input.input_id,
                    text="",
                    sequence=0,
                    extraction_notes=["empty raw_text produced no substantive observation"],
                )
            ]
            result.observations = observations

        for observation in observations:
            evidence = self._evidence_from_observation(raw_input, observation)
            lineage = self.lineage_tracker.track(raw_input, evidence)
            provenance = self.provenance_extractor.extract(
                raw_input,
                evidence,
                extracted_span=self._span_for_observation(observation),
            )
            evidence.metadata["provenance_id"] = provenance.id
            evidence.metadata["contamination_flags"] = []

            flags = self.contamination_detector.detect(
                raw_input,
                evidence,
                duplicate_source_uri=lineage.duplicate_source_uri,
                derivative_source=lineage.lineage_type is LineageType.DERIVATIVE_SOURCE,
            )
            evidence.metadata["contamination_flags"] = [
                flag.flag_type.value for flag in flags
            ]

            observation.evidence_id = evidence.id
            result.evidence_items.append(evidence)
            result.lineage_records.append(lineage)
            result.provenance_records.append(provenance)
            result.contamination_flags.extend(flags)

        result.contamination_flags = self._dedupe_flags(result.contamination_flags)
        return result

    def _extract_observations(self, raw_input: RawInput) -> list[ExtractedObservation]:
        observations: list[ExtractedObservation] = []
        for index, match in enumerate(re.finditer(r"[^.!?\n]+(?:[.!?]|\n|$)", raw_input.raw_text)):
            text = match.group(0).strip()
            if not text:
                continue
            observations.append(
                ExtractedObservation(
                    input_id=raw_input.input_id,
                    text=text,
                    sequence=index,
                    start_offset=match.start(),
                    end_offset=match.end(),
                    extraction_notes=["deterministic sentence-like span"],
                )
            )
        return observations

    def _evidence_from_observation(
        self,
        raw_input: RawInput,
        observation: ExtractedObservation,
    ) -> EvidenceItem:
        evidence_id = str(
            uuid5(
                NAMESPACE_URL,
                f"evidence:{raw_input.input_id}:{observation.sequence}:{observation.text}",
            )
        )
        source_id = raw_input.source_uri or f"unknown:{raw_input.input_id}"
        recorded_at = raw_input.collected_at or datetime(1970, 1, 1, tzinfo=timezone.utc)
        metadata = {
            "raw_input_id": raw_input.input_id,
            "raw_input_type": raw_input.input_type.value,
            "title": raw_input.title,
            "source_uri": raw_input.source_uri,
            "source_kind": raw_input.source_kind,
            "declared_event_hint": raw_input.declared_event_hint,
            "extraction_method": "deterministic_sentence_split",
            "observation_id": observation.id,
        }
        metadata.update(raw_input.metadata)

        return EvidenceItem(
            summary=observation.text,
            source_id=source_id,
            evidence_type=raw_input.input_type.value,
            category=self._category_for_source_kind(raw_input.source_kind),
            observed_at=raw_input.collected_at,
            recorded_at=recorded_at,
            id=evidence_id,
            confidence=0.5,
            tags=set(raw_input.metadata.get("tags", set())),
            metadata=metadata,
        )

    def _category_for_source_kind(self, source_kind: str) -> EvidenceCategory:
        normalized = source_kind.casefold()
        if normalized in {"official_record", "archival_document", "transcript", "primary"}:
            return EvidenceCategory.PRIMARY
        if normalized in {"forum", "repost", "social_media"}:
            return EvidenceCategory.CONTAMINATED_REPETITION
        if normalized in {"speculation", "anonymous"}:
            return EvidenceCategory.SPECULATION
        return EvidenceCategory.SECONDARY_INTERPRETATION

    def _quality_warnings(self, raw_input: RawInput) -> list[str]:
        warnings: list[str] = []
        if not raw_input.source_uri:
            warnings.append(ContaminationFlagType.MISSING_SOURCE_URI.value)
        if raw_input.collected_at is None and not raw_input.declared_event_hint:
            warnings.append(ContaminationFlagType.MISSING_DATE.value)
        if not raw_input.title:
            warnings.append(ContaminationFlagType.MISSING_TITLE.value)
        return warnings

    def _span_for_observation(
        self,
        observation: ExtractedObservation,
    ) -> tuple[int, int] | None:
        if observation.start_offset is None or observation.end_offset is None:
            return None
        return (observation.start_offset, observation.end_offset)

    def _dedupe_flags(self, flags: list[ContaminationFlag]) -> list[ContaminationFlag]:
        deduped: dict[tuple[ContaminationFlagType, str | None], ContaminationFlag] = {}
        for flag in flags:
            deduped.setdefault((flag.flag_type, flag.evidence_id), flag)
        return list(deduped.values())
