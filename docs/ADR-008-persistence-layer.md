# ADR-008: Persistence Layer

## Status

Accepted.

## Context

The framework now has evidence, provenance, lineage, memory, graph, retrieval,
reasoning, and discourse records. Long-running investigations need those
records to survive across sessions without turning saved data into a new source
of truth.

## Decision

Phase 8 adds deterministic local JSON snapshots:

- `SnapshotBuilder` creates immutable `PersistenceEnvelope` objects.
- `Serializer` converts project dataclasses to and from JSON-compatible
  dictionaries, preserving datetimes, metadata, sets, enums, and unknown fields.
- `PersistenceStore` saves and loads local JSON snapshots without network calls
  or code execution.
- `SnapshotValidator` checks schema version, record counts, checksums,
  provenance presence, and lineage presence.
- `PersistenceGuardrails` preserves semantic boundaries after load.

Snapshots include a manifest with producer, format, schema version, record
counts, deterministic snapshot id, checksum, creation time, and notes.

## Rationale

### Persistence Before Long-Running Investigation

Without persistence, each session loses evidence and reasoning state. Snapshots
make investigations auditable and repeatable before a database is introduced.

### Snapshots Are Immutable Records

A snapshot records what the framework knew at a point in time. Loading a
snapshot reconstructs records for review, but does not apply them into a live
graph, create claims, or mutate truth state.

### Loading Must Not Mutate Truth

Loaded data is data. It is never executed, never trusted automatically, and
never promoted from discourse or reasoning into evidence.

### Discourse Is Persisted Separately

Discourse records are human-review presentation artifacts. They remain separate
from evidence, claims, provenance, and graph records so narrative cannot become
source material by accident.

### Checksums Matter

Deterministic checksums help detect corrupted or edited snapshots. The checksum
is computed from canonical JSON with the checksum field blanked to avoid
self-reference.

### Unknown Fields Are Preserved

Future schema versions may add fields. Unknown fields are preserved in
`PersistenceRecord.unknown_fields` or model metadata rather than silently
dropped, making future migrations safer.

## Consequences

The project can now save and reload local JSON snapshots using only the standard
library. A future database migration can treat snapshots as the stable archival
format and import them through explicit schema migrations.
