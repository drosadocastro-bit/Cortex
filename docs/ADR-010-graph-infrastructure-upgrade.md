# ADR-010: Graph and Temporal Infrastructure Upgrade

## Status

Accepted.

## Context

The framework established epistemic foundations before adding heavier
infrastructure: provenance, lineage, contradiction preservation, association
guardrails, bounded reasoning, discourse, persistence, and evaluation.

Phase 9 introduces two lightweight dependencies, `networkx` and
`python-dateutil`, only behind deterministic wrappers.

## Decision

Add graph and temporal infrastructure:

- `GraphBackend` abstracts graph operations.
- `NetworkXGraphBackend` implements deterministic traversal over a NetworkX
  `MultiDiGraph`.
- `TimelineEngine` uses `python-dateutil` only through safe parsing wrappers.
- `TemporalReasoningHelper` compares approximate dates conservatively.
- Evaluation scenarios include graph traversal, lineage path, temporal
  ambiguity, subgraph determinism, and duplicate edge checks.

The existing in-memory `RelationshipGraphEngine` remains available.

## Rationale

### Infrastructure Comes After Guardrails

NetworkX is useful now because graph semantics are already tested. The library
adds traversal and subgraph support without replacing provenance or
contradiction rules.

### Graph Abstraction

`GraphBackend` keeps graph operations behind an interface so future graph
databases can be added without changing epistemic behavior.

### Why NetworkX

NetworkX is lightweight, local, deterministic when outputs are explicitly
sorted, and appropriate before any graph database is introduced.

### Temporal Ambiguity

`python-dateutil` can parse dates, but it must not silently fabricate precision.
The timeline wrapper treats full ISO dates as exact and month/year hints as
ranges with uncertainty notes.

### Deterministic Traversal

Traversal output is sorted by node id and edge metadata. This makes graph
reasoning testable and prevents insertion order from becoming hidden behavior.

### Minimal Dependencies

Only `networkx` and `python-dateutil` are added. Vector databases, LLM APIs,
cloud services, web UI, and autonomous agents remain out of scope.

## Consequences

The framework can now use stronger graph traversal and safer temporal parsing
while preserving provenance, contradiction visibility, lineage caution, and
uncertainty.
