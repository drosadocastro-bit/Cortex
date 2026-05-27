"""Core domain models for uncertain investigative evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


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


class EvidenceCategory(str, Enum):
    """Epistemic category for evidence or evidence-like assertions."""

    PRIMARY = "primary"
    SECONDARY_INTERPRETATION = "secondary_interpretation"
    SPECULATION = "speculation"
    CONTAMINATED_REPETITION = "contaminated_repetition"
    UNSUPPORTED_CLAIM = "unsupported_claim"


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
