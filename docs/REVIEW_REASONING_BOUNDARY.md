# Review Reasoning Boundary

This document defines how review workflow state may influence activated
context, bounded reasoning, and discourse without becoming evidence or truth.

## Core Rule

Review state may guide attention. It may not change evidentiary weight.

Claim dockets, source dockets, sessions, audit trails, and bundles can help
Cortex decide what should remain visible, but they cannot confirm a claim,
reject a source, create graph support, or alter claim confidence.

## Allowed Influence

Review workflow state may influence:

- active focus ordering
- context selection priority
- unresolved item visibility
- deferred item visibility
- provenance-gap warnings
- source-review warning visibility
- discourse annotations about review status
- uncertainty notes carried into reasoning

Examples:

- A high-priority claim docket item may be selected earlier for context.
- An unresolved contradiction may be forced to remain visible.
- A deferred source item may be shown as pending provenance.
- A reviewed item may be described as reviewed, but only as workflow state.

## Forbidden Influence

Review workflow state must not:

- mutate evidence records
- mutate claim records
- change claim matrix confidence
- create support or contradiction graph edges
- change source trust scores
- convert source risk into source rejection
- convert reviewed status into confirmation
- convert a bundle into a final report
- treat audit records as evidence

## Boundary Components

`ReviewInfluencePolicy`
: Reads `ReviewSession`, `ClaimReviewDocket`, and `SourceReviewDocket` records
and emits `ReviewInfluenceResult`. The result contains prioritized ids,
must-include ids, deferred ids, unresolved ids, provenance-gap ids,
source-review warning ids, uncertainty notes, discourse annotations, and
warnings.

`ReviewContextAdapter`
: Copies an `ActivatedContext` and adds review influence as uncertainty notes.
It does not infer object type from ids and does not mutate supplied records.

`ContextWindowBuilder`
: May use `ReviewInfluenceResult` to include matching evidence, claims, or
memories when typed record maps are supplied. This affects context visibility
only.

`CognitiveReasoningEngine`
: May accept review influence and pass it into context construction. The
reasoning output still treats review state as uncertainty or review-boundary
notes, not confirmation.

## Analyst Loop Contract

```text
review dockets
-> working memory
-> review session decisions
-> review influence hints
-> bounded context selection
-> reasoning uncertainty notes
-> discourse review annotations
```

At no point in this loop should review decisions be applied back into evidence,
claim, source, graph, or provenance state.

## Testing Expectations

Tests should prove:

- reviewed claims do not gain confidence
- deferred items remain visible
- source-review risk does not reject a source
- session decisions do not create graph edges
- review bundles do not alter claim matrix state
- discourse can mention review state without mutating evidence
- review priority changes ordering only
- provenance gaps remain visible

These tests are behavioral checks for epistemic separation. They do not validate
real-world conclusions.
