# ADR-035: Predictive Memory And Expectation Layer

## Status

Accepted.

## Context

Cortex is intentionally not a truth engine. It also should not be merely a
vector-retrieval system. A memory framework can preserve more structure than
similarity: provenance, lineage, contradiction, recurrence, decay, uncertainty,
and review history.

Phase 33 adds a deterministic predictive-memory layer inspired by predictive
coding as a design metaphor: memory can organize past structure into bounded
expectations about what may deserve attention next. This does not make Cortex
conscious, agentic, or able to predict reality.

## Decision

Add `PredictiveMemoryEngine` and supporting records:

- `ExpectationTrace`
- `PredictionCandidate`
- `PredictionError`
- `SurpriseSignal`
- `PredictiveMemoryResult`
- `ExpectationGuardrails`
- `PredictiveReviewAdapter`

The engine examines existing `MemoryRecord` structure and deterministically
surfaces expectations such as:

- missing provenance likely needs review
- contradiction pressure likely remains relevant
- repeated normalized memory keys may indicate duplicate or lineage echo review
- stale memories may need refresh or archival review
- unexpected incoming gaps or contradictions should raise surprise signals

## Boundary Rules

Predictive memory may influence:

- review attention
- context visibility
- uncertainty notes
- surprise/anomaly review queues

Predictive memory must not:

- create evidence
- confirm claims
- disprove incoming records
- increase memory strength
- apply decay
- merge memories
- create graph edges
- turn recurrence into corroboration
- treat expectation as truth

## Relationship To Dream Replay

Dream replay consolidates unresolved memory offline. Predictive memory organizes
prior structure into review expectations. Both are internal cognitive artifacts.
Neither is evidence, confirmation, or source trust.

## Consequences

Cortex gains an anticipatory review mechanism without adding LLM calls, vector
databases, autonomous agents, or truth prediction. The system can now say,
"given the current memory structure, these review needs are likely to matter,"
while preserving the boundary that likely-to-matter is not true.

## Failure Mode Addressed

RAG and vector retrieval can over-emphasize textual similarity. Predictive memory
addresses a different failure mode: losing the expected unresolved work implied
by memory state. It helps preserve provenance gaps, contradiction pressure,
recurrence, and stale-memory review needs as active attention signals.
