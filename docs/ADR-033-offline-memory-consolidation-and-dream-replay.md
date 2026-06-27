# ADR-033: Offline Memory Consolidation And Dream Replay

## Status

Accepted.

## Context

Cortex already has memory decay, duplicate-memory merging, contradiction
pressure, working memory, review sessions, persistence, and reality-boundary
checks. Those mechanisms are useful, but they operate as separate bounded
pieces. A long-running cognitive framework also needs a rest-cycle concept: a
way to replay existing memory state offline and surface what may need review
without creating new evidence or deciding truth.

This phase introduces dream replay as an internal consolidation layer. The word
"dream" is used in the memory-replay sense, not as hallucination, imagination,
or autonomous inference.

## Decision

Add a deterministic `DreamReplayEngine` that consumes existing `MemoryRecord`
objects and emits a `DreamReplayResult` containing:

- a `DreamArtifact`
- `MemoryConsolidationNote` records
- `ConsolidationRecommendation` records
- duplicate candidate groups
- stale, archival, and contradiction memory ids
- warnings and limitations

Dream replay is read-only. It does not call live LLMs, vector databases,
external APIs, memory activation, memory decay mutation, duplicate merge
mutation, graph mutation, or claim confirmation.

## Boundary Rules

Dream replay may:

- identify stale memories
- identify duplicate-key memory candidates
- preserve archival memory visibility
- preserve contradiction pressure visibility
- expose missing evidence references
- recommend later review, refresh, merge review, archival review, or uncertainty
  preservation

Dream replay must not:

- create evidence
- create claims
- create graph edges
- confirm or reject claims
- treat duplicate replay as corroboration
- reactivate archival memories
- apply decay automatically
- merge memories automatically
- resolve contradictions
- mutate source trust or claim confidence

## Why This Belongs After Phase 30

Phase 30 reorganized the documentation map. Dream replay adds a brain-inspired
mechanism only after the framework has memory boundaries, review boundaries,
persistence boundaries, evaluation boundaries, adversarial baselines, and a
clear scope map.

## Consequences

The framework gains an offline rest-cycle concept without changing the meaning
of memory strength, decay, merging, or contradiction pressure.

Dream artifacts are internal cognitive artifacts. They are useful review inputs,
but they are not evidence, not external observations, and not conclusions.

## Failure Mode Addressed

Without a bounded consolidation layer, future phases could scatter refresh,
merge-review, stale-memory, and contradiction-replay behavior across unrelated
workflow modules. This ADR keeps that behavior in one deterministic place while
preserving the rule that attention and repetition are not truth.
