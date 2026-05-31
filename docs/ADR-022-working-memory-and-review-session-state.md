# ADR-022: Working Memory And Review Session State

Status: Accepted

## Context

Cortex can now produce claim review dockets and source review dockets. What was
missing was an explicit model of the active review session: what is currently
in focus, what has been reviewed, what has been deferred, what remains
unresolved, and what changed between review passes.

This layer should support future UI and longer investigations without becoming
an autonomous agent or a truth state manager.

## Decision

Add `WorkingMemoryEngine`, `ReviewSessionEngine`, and `SessionFormatter`.

Working memory accepts claim dockets, source dockets, activated context,
reasoning output, and discourse output. It builds `ReviewSessionState` with
active focus ids, active docket ids, reviewed items, deferred items, unresolved
items, contradiction ids, and uncertainty notes.

Review sessions record `ReviewDecision` annotations and `SessionDelta` updates.
Decisions are limited to review annotations such as reviewed, deferred, keep
unresolved, request more provenance, or request source review.

## Why Working Memory Exists

The framework needs a bounded active workspace before UI or live inference is
added. Working memory tells Cortex what is currently being held for review
without reinterpreting the underlying evidence, claims, sources, or graph.

## Why Session Decisions Are Not Truth

A human may review an item, defer it, or request more provenance. Those actions
do not confirm claims, reject sources, resolve contradictions, or mutate
evidence. They are annotations about review workflow.

## Why Deferred Items Stay Visible

Deferral is not deletion and not irrelevance. Deferred items remain visible in
session state so uncertainty is not silently lost between review passes.

## Consequences

Positive:

- Future UI can render session state instead of inventing behavior.
- Reviewed, deferred, and unresolved items are tracked deterministically.
- Contradictions and uncertainty remain active across review passes.
- Session deltas make review changes inspectable.

Tradeoffs:

- Session timestamps are deterministic by default for testability.
- This is not a collaboration, permissions, or user-account system.
- Future persistence integration may need snapshot support for session records.

## Non-Goals

- No UI.
- No autonomous agent.
- No claim confirmation.
- No source rejection.
- No graph edge creation.
- No mutation of evidence, claims, source trust, or graph records.
