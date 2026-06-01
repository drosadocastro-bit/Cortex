# UI Readiness Notes

The future Cortex UI should be a quiet investigative review cockpit. It should
render existing review state rather than invent new reasoning behavior.

## Design Posture

The UI should feel like a careful review workspace:

- evidence-first
- provenance-visible
- uncertainty-preserving
- contradiction-friendly
- session-oriented
- calm and dense enough for repeated review

It should not feel like:

- an answer engine
- a chatbot-first interface
- a truth dashboard
- an operational analysis console
- a polished conclusion generator

## First Screen Concept

The first screen should open into the active review session, not a landing page.

Suggested layout:

- Left rail:
  - sessions
  - active focus
  - review queue
  - demo workspace selector
- Center workspace:
  - claim review docket tab
  - source review docket tab
  - review bundle tab
  - working memory tab
- Right rail:
  - provenance
  - lineage
  - uncertainty notes
  - contradictions
  - audit trail
- Bottom action strip:
  - reviewed
  - defer
  - request provenance
  - request source review
  - keep unresolved

## Non-Negotiable Boundaries

The UI must preserve these labels and separations:

- support is not confirmation
- contradiction is not disproof
- source review is not source truth
- reviewed is not confirmed
- deferred is not discarded
- audit trail is not evidence
- bundle is not final report
- demo data is synthetic only

## First UI Fixture

The first UI fixture should be `DemoWorkspaceBuilder`. It provides a complete
synthetic session with claim dockets, source dockets, audit trail, review
bundle, contradictions, uncertainty, contamination, and provenance references.

No real data should be used for the first UI.

## Suggested Phase Before UI

Before building screens, add a UI readiness API/view-model layer that converts
existing records into stable display models. The UI should consume those models
instead of reaching into every internal dataclass directly.
