# ADR-002: Cognitive Memory Dynamics

## Status

Accepted.

## Context

The framework needs memory behavior that supports uncertain investigation
without converting repeated statements into truth. Phase 0 supported duplicate
merging and simple decay. Phase 1 adds activation, archival transition,
semantic compression, and contradiction pressure.

## Decision

Memory records are weighted cognitive structures. They evolve through
deterministic activation, decay, compression, and contradiction pressure.

## Why Memory Decay Exists

Unused memories should become less prominent over time so the system does not
surface stale, weak, or low-use records as strongly as repeatedly useful ones.
Decay changes prominence, not truth status.

## Why Repetition Reinforces Instead of Duplicating

Repeated consistent memories increase activation and strength, but duplicate
records merge instead of accumulating. This prevents duplicate evidence from
inflating the apparent size of a claim.

## Why Contradiction Is Preserved

Contradiction is investigative signal. The system records pressure and links
conflicting memories, but it does not choose a winner automatically. Preserving
conflict keeps uncertainty visible for later review.

## Why Archival State Is Preferred Over Deletion

Weak unused memories may become archival, but they are not deleted. Archival
state protects provenance, supports later reactivation, and avoids silent loss
of potentially important context.

## Consequences

- Memory behavior remains deterministic and testable.
- Repetition can improve recall but cannot create certainty.
- Contradictions remain available as unresolved structure.
- Archival records remain inspectable and can return to active status.
