# ADR-023: Session Persistence And Audit Trail

Status: Accepted

## Context

Phase 20 added working memory and review session state. Review sessions need to
survive across runs, and review actions need an audit trail. Persistence must
not turn session annotations into evidence, claim confirmation, source
rejection, or graph mutation.

## Decision

Add `SessionAuditLogger`, `SessionPersistenceStore`, and
`SessionAuditFormatter`.

Session persistence stores `ReviewSession` records and `SessionAuditTrail`
records in deterministic local JSON. Each envelope includes a manifest,
schema version, record counts, deterministic snapshot id, and checksum.

Audit records can capture session start, resume, decision, defer, review, and
report-formatting events. They are workflow records only.

## Why This Exists Before UI

Future UI should render persisted session state, dockets, decisions, deltas,
and audit events. It should not invent its own hidden state semantics. Saving
session state first makes the future interface simpler and safer.

## Why Audit Is Not Evidence

An audit event says what the review workflow did. It does not say that an
external event happened, that a claim is true, or that a source is accepted or
rejected.

## Consequences

Positive:

- Review sessions can round-trip deterministically.
- Decisions, deferred items, and unresolved items remain inspectable.
- Audit trails preserve workflow history.
- Checksums detect corrupted session payloads.

Tradeoffs:

- Session persistence has its own small envelope format instead of reusing the
  evidence snapshot envelope directly.
- Session timestamps are deterministic by default for testability.
- Future UI may need richer event types, but those must remain workflow
  annotations.

## Non-Goals

- No UI.
- No database.
- No network calls.
- No execution of loaded data.
- No automatic creation of evidence, claims, sources, graph edges, or truth
  state during load.
