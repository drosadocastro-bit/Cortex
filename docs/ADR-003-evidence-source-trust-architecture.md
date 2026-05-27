# ADR-003: Evidence and Source Trust Architecture

## Status

Accepted.

## Context

The memory system can preserve uncertainty, merge duplicates, decay unused
records, and track contradiction pressure. Without source trust architecture,
however, repeated low-quality retellings could still become over-prominent.

## Decision

Add deterministic engines for source trust, lineage, contamination detection,
and corroboration assessment.

## Why Source Trust Is Separate from Memory Strength

Memory strength indicates cognitive prominence. It does not mean a record is
true, well sourced, or independently corroborated. Source trust needs separate
fields and scores so a frequently activated memory can still be treated with
caution.

## Why Lineage Is Required

Copied claims often appear independent when they are actually retellings of the
same source. Lineage lets the system identify source ancestry and avoid treating
large copy chains as independent corroboration.

## Why Contamination Is Flagged, Not Deleted

Contamination is itself useful investigative metadata. Fictionalization,
speculative escalation, ambiguous sourcing, and citation loops should increase
risk and review pressure, not erase the underlying record.

## Why Corroboration Is a Layer

Corroboration depends on independence. A repeated source and an independent
source are different epistemic signals, even when they make similar claims.
Keeping corroboration as a separate layer makes that distinction testable.

## Consequences

- Trust scoring remains deterministic and bounded.
- Repeated retellings do not become independent evidence.
- Unsupported and contaminated records remain preserved but risk-marked.
- Future ingestion can attach lineage and trust metadata without changing memory
  semantics.
