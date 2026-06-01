# ADR-027: Workflow View Models And Demo Presentation Contract

## Status

Accepted.

## Context

Cortex has a bounded review workflow, session state, audit trails, review
bundles, and a synthetic demo workspace. A future UI needs stable display
objects, but UI code should not reach into every internal dataclass or invent
parallel reasoning behavior.

The risk is presentation drift: display priority could become confidence,
source risk could look like rejection, review bundles could look like final
reports, and demo output could look like real-world validation.

## Decision

Add read-only presentation/view models:

- `WorkflowStageView`
- `ClaimReviewCardView`
- `SourceReviewCardView`
- `SessionTimelineView`
- `BundlePreviewView`
- `ReviewDashboardView`
- `DemoPresentation`
- `PresentationWarning`

Add builders and guardrails:

- `PresentationBuilder`
- `PresentationGuardrails`
- `DemoPresentationBuilder`

These components adapt existing review workflow state into deterministic,
display-ready records. They do not build UI, mutate state, create evidence,
change claim confidence, create graph edges, or add review decisions.

## Consequences

Future UI work can consume a stable presentation contract instead of coupling
directly to every cognitive and workflow module.

Presentation is now clearly a display layer:

- display priority is not truth confidence
- claim cards are not claim status mutation
- source cards are not source acceptance or rejection
- audit timelines are not evidence
- bundle previews are not final reports
- demo presentations are synthetic fixtures only

## Non-Goals

- No frontend framework is added.
- No web UI is added.
- No charts, styling, or interactive controls are added.
- No real data is ingested.
- No LLM, vector database, network call, or autonomous behavior is added.

## Guardrails

`PresentationGuardrails` checks for missing synthetic labels, missing
limitations, missing provenance, hidden contradictions, and certainty-inflating
language.

The first UI should render these view models without adding reasoning logic.
