# ADR-034: Dream Replay Boundary Integration

## Status

Accepted.

## Context

Phase 31 introduced offline memory consolidation and dream replay. That layer can
surface duplicate candidates, stale memories, archival memories, contradiction
pressure, provenance gaps, and review recommendations. The next risk is subtle:
if dream output is allowed to shape review workflows, it could be mistaken for
new evidence, confirmation, corroboration, or memory truth amplification.

Cortex needs a narrow wake-up path: dream artifacts may influence review
visibility, but they must not become reality claims.

## Decision

Add a bounded dream-to-review boundary with three small components:

- `DreamInfluencePolicy` converts `DreamReplayResult` into the existing
  `ReviewInfluenceResult` contract.
- `DreamReviewAdapter` exposes replayed memories as `AttentionCandidate` records
  so attention ordering can include dream-visible items.
- `DreamBoundaryGuardrails` emits explicit warnings and blocks automatic
  evidence promotion.

This extends the existing review influence pathway instead of creating a second
parallel workflow system.

## Boundary Rules

Dream replay may influence:

- review prioritization
- context visibility
- discourse annotations
- unresolved item visibility
- contradiction visibility
- provenance-gap visibility

Dream replay must not:

- create evidence
- confirm claims
- create graph edges
- merge memories
- apply decay
- increase memory strength
- resolve contradictions
- treat duplicate replay as corroboration
- mutate source trust, claim confidence, or memory records

## Consequences

Dream artifacts can now wake up into review attention without bypassing Cortex's
reality boundary. Review influence remains explicit and auditable through
`ReviewInfluenceResult`.

The design also keeps future UI, persistence, live inference, or scheduling work
from treating dream output as a hidden source of authority.

## Failure Mode Addressed

The main failure mode is dream laundering: an internal replay artifact becomes a
review signal, then silently becomes evidence, support, or confidence. Phase 32
keeps that path blocked by preserving dream output as review context only.
