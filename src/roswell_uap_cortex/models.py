"""Core domain models for uncertain investigative evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class ClaimStatus(str, Enum):
    """Resolution state for claims without asserting truth."""

    UNASSESSED = "unassessed"
    SUPPORTED = "supported"
    CONTESTED = "contested"
    CONTRADICTED = "contradicted"
    RETRACTED = "retracted"


class GraphNodeType(str, Enum):
    """Types of nodes available to the investigative graph."""

    EVIDENCE = "evidence"
    CLAIM = "claim"
    SOURCE = "source"
    EVENT = "event"
    ENTITY = "entity"
    MEMORY = "memory"


class RelationshipType(str, Enum):
    """Deterministic relationship types in the investigative graph."""

    MENTIONS = "mentions"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFERENCES = "references"
    SAME_EVENT_CANDIDATE = "same_event_candidate"
    TEMPORAL_BEFORE = "temporal_before"
    TEMPORAL_AFTER = "temporal_after"
    DERIVED_FROM = "derived_from"
    DUPLICATE_OF = "duplicate_of"


class TimelineDatePrecision(str, Enum):
    """How precise an event date is known to be."""

    EXACT = "exact"
    MONTH = "month"
    YEAR = "year"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class ClaimMatrixStatus(str, Enum):
    """Claim matrix status labels that preserve unresolved uncertainty."""

    UNSUPPORTED = "unsupported"
    WEAKLY_SUPPORTED = "weakly_supported"
    CONTESTED = "contested"
    SUPPORTED = "supported"
    UNRESOLVED = "unresolved"


class AssociationLabel(str, Enum):
    """Association labels are retrieval hints, not relationship confirmations."""

    POSSIBLE_ASSOCIATION = "possible_association"
    WEAK_ASSOCIATION = "weak_association"
    CONTESTED_ASSOCIATION = "contested_association"


class EvidenceCategory(str, Enum):
    """Epistemic category for evidence or evidence-like assertions."""

    PRIMARY = "primary"
    SECONDARY_INTERPRETATION = "secondary_interpretation"
    SPECULATION = "speculation"
    CONTAMINATED_REPETITION = "contaminated_repetition"
    UNSUPPORTED_CLAIM = "unsupported_claim"


class RawInputType(str, Enum):
    """Supported raw ingestion input types."""

    DOCUMENT = "document"
    TRANSCRIPT = "transcript"
    NOTE = "note"
    IMAGE_METADATA = "image_metadata"
    VIDEO_METADATA = "video_metadata"
    UNKNOWN = "unknown"


class LineageType(str, Enum):
    """Ingestion lineage classification."""

    PRIMARY_SOURCE = "primary_source"
    SECONDARY_SOURCE = "secondary_source"
    DERIVATIVE_SOURCE = "derivative_source"
    UNKNOWN_LINEAGE = "unknown_lineage"


class ContaminationFlagType(str, Enum):
    """Deterministic contamination and source-quality warnings."""

    MISSING_DATE = "missing_date"
    MISSING_SOURCE_URI = "missing_source_uri"
    MISSING_TITLE = "missing_title"
    DERIVATIVE_SOURCE = "derivative_source"
    REPEATED_SOURCE_URI = "repeated_source_uri"
    ANONYMOUS_SOURCE = "anonymous_source"
    SPECULATIVE_LANGUAGE = "speculative_language"
    FICTIONAL_CONTAMINATION_TERMS = "fictional_contamination_terms"
    WEAK_CHAIN_OF_CUSTODY = "weak_chain_of_custody"


class ConfidenceBand(str, Enum):
    """Context-support band for reasoning output, not truth confidence."""

    INSUFFICIENT_CONTEXT = "insufficient_context"
    LOW = "low"
    MEDIUM = "medium"
    HIGH_CONTEXT_SUPPORT = "high_context_support"
    CONTESTED = "contested"


class ReasoningWarningType(str, Enum):
    """Typed guardrail warnings for bounded reasoning."""

    ASSOCIATION_NOT_CONFIRMATION = "association_not_confirmation"
    CONTRADICTION_VISIBLE = "contradiction_visible"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    MISSING_PROVENANCE = "missing_provenance"
    SAME_LINEAGE_REPETITION = "same_lineage_repetition"
    FICTIONAL_CONTAMINATION = "fictional_contamination"
    SPECULATIVE_HYPOTHESIS = "speculative_hypothesis"


@dataclass(slots=True)
class EvidenceItem:
    """A source-backed artifact or observation, never a truth claim by itself."""

    summary: str
    source_id: str
    evidence_type: str
    category: EvidenceCategory = EvidenceCategory.UNSUPPORTED_CLAIM
    observed_at: datetime | None = None
    recorded_at: datetime = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid4()))
    confidence: float = 0.5
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RawInput:
    """Raw sensory input before normalization into evidence records."""

    input_id: str
    input_type: RawInputType | str = RawInputType.UNKNOWN
    title: str | None = None
    raw_text: str = ""
    source_uri: str | None = None
    source_kind: str = "unknown"
    collected_at: datetime | None = None
    declared_event_hint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.input_type, str):
            self.input_type = RawInputType(self.input_type)


@dataclass(slots=True)
class ExtractedObservation:
    """A deterministic observation span extracted from raw text."""

    input_id: str
    text: str
    sequence: int
    id: str = ""
    start_offset: int | None = None
    end_offset: int | None = None
    evidence_id: str | None = None
    extraction_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid5(NAMESPACE_URL, f"observation:{self.input_id}:{self.sequence}:{self.text}"))


@dataclass(slots=True)
class ProvenanceRecord:
    """Mandatory provenance for ingested evidence."""

    evidence_id: str
    source_uri: str
    source_kind: str
    ingestion_method: str
    extraction_method: str
    original_input_id: str
    id: str = ""
    extracted_span: tuple[int, int] | None = None
    page_number: int | None = None
    timestamp_range: tuple[str, str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid5(NAMESPACE_URL, f"provenance:{self.original_input_id}:{self.evidence_id}"))


@dataclass(slots=True)
class SourceLineageRecord:
    """Lineage assigned during ingestion so repetition remains visible."""

    evidence_id: str
    source_id: str
    lineage_id: str
    lineage_type: LineageType = LineageType.UNKNOWN_LINEAGE
    source_uri: str | None = None
    parent_source_id: str | None = None
    derived_from: str | None = None
    duplicate_source_uri: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ContaminationFlag:
    """A deterministic warning about source quality or contamination risk."""

    flag_type: ContaminationFlagType
    input_id: str
    evidence_id: str | None = None
    source_uri: str | None = None
    note: str = ""


@dataclass(slots=True)
class IngestionResult:
    """Auditable output of deterministic raw-input normalization."""

    raw_input_id: str
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    observations: list[ExtractedObservation] = field(default_factory=list)
    provenance_records: list[ProvenanceRecord] = field(default_factory=list)
    lineage_records: list[SourceLineageRecord] = field(default_factory=list)
    contamination_flags: list[ContaminationFlag] = field(default_factory=list)
    source_trust_hints: dict[str, Any] = field(default_factory=dict)
    ingestion_warnings: list[str] = field(default_factory=list)
    ingestion_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Claim:
    """An assertion derived from evidence, with explicit uncertainty."""

    text: str
    evidence_ids: set[str] = field(default_factory=set)
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ClaimStatus = ClaimStatus.UNASSESSED
    confidence: float = 0.5
    uncertainty_notes: str = ""
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class EntityNode:
    """A person, organization, place, object, or concept mentioned by evidence."""

    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    entity_type: str = "unknown"
    aliases: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EventNode:
    """A dated or undated event without fabricated chronology."""

    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    event_date: date | None = None
    earliest_possible_date: date | None = None
    latest_possible_date: date | None = None
    date_precision: TimelineDatePrecision = TimelineDatePrecision.UNKNOWN
    date_note: str = ""
    evidence_ids: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimNode:
    """A graph-ready claim separated from its supporting evidence."""

    text: str
    canonical_topic: str
    id: str = field(default_factory=lambda: str(uuid4()))
    evidence_ids: set[str] = field(default_factory=set)
    status: ClaimMatrixStatus = ClaimMatrixStatus.UNSUPPORTED
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceNode:
    """A source as a first-class graph node."""

    source_id: str
    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    source_type: str = "unknown"
    trust_score: float = 0.5
    lineage_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RelationshipEdge:
    """A provenance-carrying relationship between two graph nodes."""

    from_node_id: str
    to_node_id: str
    relation: RelationshipType
    source_id: str
    confidence: float = 0.5
    evidence_ids: set[str] = field(default_factory=set)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class AssociationScore:
    """Deterministic association signals; not a truth score."""

    lexical_overlap: float = 0.0
    tag_overlap: float = 0.0
    entity_overlap: float = 0.0
    timeline_proximity: float = 0.0
    source_independence: float = 0.0
    contradiction_penalty: float = 0.0
    final_association_score: float = 0.0


@dataclass(slots=True)
class AssociationCandidate:
    """A possible retrieval association with inspectable reasons."""

    record_id: str
    record_type: str
    label: str
    score: AssociationScore
    association_label: AssociationLabel = AssociationLabel.POSSIBLE_ASSOCIATION
    association_reason: list[str] = field(default_factory=list)
    memory_ids: set[str] = field(default_factory=set)
    claim_ids: set[str] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)
    entity_ids: set[str] = field(default_factory=set)
    source_id: str | None = None
    lineage_id: str | None = None
    claim_status: ClaimMatrixStatus | None = None
    uncertainty_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalContext:
    """Optional query-side context for deterministic associative retrieval."""

    query: str
    query_tags: set[str] = field(default_factory=set)
    query_entity_ids: set[str] = field(default_factory=set)
    query_canonical_topics: set[str] = field(default_factory=set)
    query_date: date | None = None
    source_id: str | None = None
    lineage_id: str | None = None


@dataclass(slots=True)
class ActivatedContext:
    """A focused retrieval context for downstream deterministic reasoning."""

    activated_memory_ids: set[str] = field(default_factory=set)
    activated_claim_ids: set[str] = field(default_factory=set)
    activated_evidence_ids: set[str] = field(default_factory=set)
    activated_entity_ids: set[str] = field(default_factory=set)
    weak_associations: list[AssociationCandidate] = field(default_factory=list)
    contested_associations: list[AssociationCandidate] = field(default_factory=list)
    uncertainty_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class UncertaintyNote:
    """A structured uncertainty note carried through reasoning."""

    note: str
    related_ids: set[str] = field(default_factory=set)
    severity: str = "caution"


@dataclass(slots=True)
class ReasoningWarning:
    """A guardrail warning emitted by reasoning."""

    warning_type: ReasoningWarningType
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ReasoningObservation:
    """A bounded observation made from supplied context only."""

    text: str
    context_ids: set[str] = field(default_factory=set)
    speculative: bool = False


@dataclass(slots=True)
class ReasoningContext:
    """Compact structured context passed into local reasoning."""

    activated_context: ActivatedContext
    selected_candidates: list[AssociationCandidate] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    claims: list[ClaimNode] = field(default_factory=list)
    memories: list["MemoryRecord"] = field(default_factory=list)
    provenance_records: list[ProvenanceRecord] = field(default_factory=list)
    lineage_records: list[SourceLineageRecord] = field(default_factory=list)
    uncertainty_notes: list[UncertaintyNote] = field(default_factory=list)


@dataclass(slots=True)
class ReasoningRequest:
    """A bounded local reasoning request."""

    query: str
    activated_context: ActivatedContext
    candidates: list[AssociationCandidate] = field(default_factory=list)
    max_context_items: int = 8


@dataclass(slots=True)
class ReasoningOutput:
    """Structured local reasoning output; confidence band is not truth confidence."""

    observations: list[ReasoningObservation] = field(default_factory=list)
    supporting_context_ids: set[str] = field(default_factory=set)
    contested_context_ids: set[str] = field(default_factory=set)
    uncertainty_notes: list[UncertaintyNote] = field(default_factory=list)
    reasoning_warnings: list[ReasoningWarning] = field(default_factory=list)
    possible_hypotheses: list[ReasoningObservation] = field(default_factory=list)
    confidence_band: ConfidenceBand = ConfidenceBand.INSUFFICIENT_CONTEXT
    provenance_summary: str = ""
    requires_review: bool = False


@dataclass(slots=True)
class SourceTrust:
    """Trust metadata for a source, separate from individual evidence confidence."""

    source_id: str
    reliability: float = 0.5
    transparency: float = 0.5
    corroboration_history: float = 0.5
    source_authority: float = 0.5
    chain_of_custody: float = 0.5
    publication_distance: float = 0.5
    redaction_level: float = 0.0
    independent_corroboration: float = 0.0
    media_type: str = "unknown"
    contamination_flags: list[str] = field(default_factory=list)
    source_trust_score: float = 0.5
    source_risk_score: float = 0.5
    uncertainty_notes: str = ""
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class EvidenceLineageRecord:
    """A deterministic source lineage node for a claim or evidence item."""

    source_id: str
    claim_key: str
    id: str = field(default_factory=lambda: str(uuid4()))
    original_source_id: str | None = None
    parent_source_id: str | None = None
    source_kind: str = "unknown"
    transformations: list[str] = field(default_factory=list)
    contamination_flags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.original_source_id is None:
            self.original_source_id = self.source_id


@dataclass(slots=True)
class ContaminationReport:
    """Flags contamination risk without deleting or resolving the record."""

    record_id: str
    flags: list[str] = field(default_factory=list)
    risk_score: float = 0.0


@dataclass(slots=True)
class CorroborationAssessment:
    """Distinguish independent corroboration from repeated sourcing."""

    claim_key: str
    independent_source_ids: list[str] = field(default_factory=list)
    repeated_source_ids: list[str] = field(default_factory=list)
    independent_count: int = 0
    repeated_count: int = 0
    corroboration_score: float = 0.0


@dataclass(slots=True)
class MemoryRecord:
    """A bounded memory with provenance, decay state, and duplicate merge support."""

    content: str
    evidence_ids: set[str] = field(default_factory=set)
    id: str = field(default_factory=lambda: str(uuid4()))
    normalized_key: str | None = None
    strength: float = 0.5
    memory_strength: float = 0.5
    decay_rate: float = 0.03
    contradiction_pressure: float = 0.0
    archival: bool = False
    access_count: int = 0
    activation_count: int = 0
    consistency_count: int = 1
    created_at: datetime = field(default_factory=utc_now)
    last_accessed_at: datetime = field(default_factory=utc_now)
    last_activated_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    linked_memory_ids: list[str] = field(default_factory=list)
    needs_review: bool = False
    uncertainty_preserved: bool = False
    source_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.normalized_key is None:
            self.normalized_key = self.content_key(self.content)
        if self.memory_strength == 0.5 and self.strength != 0.5:
            self.memory_strength = self.strength
        self.strength = self.memory_strength

    @staticmethod
    def content_key(content: str) -> str:
        return " ".join(content.casefold().strip().split())


@dataclass(slots=True)
class GraphNode:
    """A graph node for evidence-first investigative reasoning."""

    node_type: GraphNodeType
    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    related_ids: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Contradiction:
    """An explicit unresolved conflict between claims or evidence records."""

    subject_id: str
    conflicting_id: str
    reason: str
    id: str = field(default_factory=lambda: str(uuid4()))
    severity: float = 0.5
    resolved: bool = False
    created_at: datetime = field(default_factory=utc_now)
