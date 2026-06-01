# ADR-025: Synthetic Demo Workspace

Status: Accepted

## Context

Cortex now has enough deterministic infrastructure to show a complete review
path. A demo is useful for documentation, future UI, regression tests, and
maintainer understanding. It must not use real UAP data or imply real-world
validation.

## Decision

Add `DemoWorkspaceBuilder` and `DemoWorkspaceGuardrails`.

The demo workspace uses tiny synthetic raw inputs and runs the canonical path:

```text
raw inputs
-> ingestion
-> evidence / provenance / lineage / contamination
-> candidate claims
-> normalized claims
-> claim evaluation
-> claim review docket
-> source review docket
-> working memory session
-> audit trail
-> review bundle
```

The synthetic fixture includes:

- a primary-style note
- a direct contradiction
- a derivative repost
- speculative contamination terms
- an incomplete anonymous source

## Why Synthetic Only

The demo exists to exercise architecture, not to investigate real events. It
must never contain real UAP data or external-source claims. The guardrail
requires source ids to use synthetic or unknown demo identifiers.

## Why This Matters Before UI

A future UI needs safe, stable data to render. The demo workspace gives the UI
a known review session, docket set, audit trail, and bundle without touching
real data.

## Non-Goals

- No real UAP ingestion.
- No UI.
- No LLM/API calls.
- No vector database.
- No truth claims.
- No graph edge creation.
