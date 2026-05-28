# ADR-005: Evidence Ingestion and Provenance

## Status

Accepted.

## Context

Before the framework can reason over evidence, it needs a sensory intake layer:
a deterministic way to convert raw documents, notes, transcripts, and metadata
into normalized evidence records.

Ingestion is risky because normalization can accidentally become interpretation.
If provenance, lineage, or contamination warnings are lost at intake time, later
graph, timeline, claim-matrix, retrieval, or vector layers may appear more
certain than the source material permits.

## Decision

Phase 5 adds deterministic ingestion with mandatory provenance:

- `RawInput` represents raw sensory material before reasoning.
- `IngestionNormalizer` extracts sentence-like observations without LLMs.
- `EvidenceItem` records are created from observations.
- `ProvenanceExtractor` attaches source URI, source kind, ingestion method,
  extraction method, original input id, span, page, and timestamp metadata.
- `LineageTracker` assigns lineage ids and marks primary, secondary,
  derivative, duplicate, or unknown lineage.
- `ContaminationDetector` attaches rule-based warning flags.

Ingestion does not create claims, confirm claims, or create graph edges.

## Rationale

### Ingestion Is The Sensory Layer

Raw inputs are like sensory memory. They are the first landing zone for material
that may later become evidence, memory, graph context, or claim support. At this
stage, the system records what was observed and where it came from.

### Raw Inputs Are Normalized Before Reasoning

Reasoning engines should not operate directly on arbitrary raw text. Normalized
evidence records make later behavior deterministic, auditable, and testable.

### Provenance Is Mandatory

Every ingested evidence item must have provenance. Missing source information is
preserved as an explicit warning and represented with an `unknown:` source URI,
not silently ignored.

### Contamination Flags Are Warnings

Flags such as `speculative_language`, `fictional_contamination_terms`, or
`weak_chain_of_custody` are not truth judgments. They are review signals that
help later engines avoid false confidence.

### Ingestion Must Not Confirm Claims

An ingested sentence can become an evidence item, but ingestion does not decide
that a claim is supported. Claim support belongs to later claim-matrix and graph
reasoning, with provenance and contradiction visible.

### Source Lineage Comes Before Graph And Vector Reasoning

Lineage must be visible before graph or vector retrieval can responsibly compare
records. Same-lineage repetition should not become independent corroboration,
and derivative sources should remain traceable to their parent source.

## Consequences

The framework can now ingest small synthetic fixtures into deterministic
evidence, provenance, lineage, and contamination outputs. Future ingestion can
expand input formats, but it must preserve this no-confirmation boundary.
