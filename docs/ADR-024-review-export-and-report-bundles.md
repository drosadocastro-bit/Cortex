# ADR-024: Review Export And Report Bundles

Status: Accepted

## Context

Cortex can now build review sessions, persist them, and audit workflow events.
The next step is an exportable review bundle that can be shared or rendered by
a future UI without becoming a final report or a conclusion.

## Decision

Add `ReviewBundleBuilder`, `ReviewBundleFormatter`, and
`ReviewBundleGuardrails`.

A review bundle contains structured sections for:

- session summary
- active focus
- claim review dockets
- source review dockets
- unresolved items
- deferred items
- uncertainty notes
- contradictions
- provenance and citations
- audit trail
- limitations

## Why This Is Not A Final Report

The bundle is a review packet. It exports the state of review, not the truth of
the underlying claims. It must preserve uncertainty, contradiction, provenance,
source risk, deferred items, and audit history.

## Why Guardrails Are Needed

Exported Markdown can look authoritative. `ReviewBundleGuardrails` checks for
certainty-inflating language and missing bundle sections so the export does not
quietly become a polished conclusion.

## UI Implication

A future UI should render these same bundle sections interactively. It should
not invent different semantics for sessions, dockets, audit trails, or
limitations.

## Non-Goals

- No UI.
- No final report generation.
- No claim confirmation.
- No source rejection.
- No evidence mutation.
- No graph edge creation.
- No LLM/API calls.
