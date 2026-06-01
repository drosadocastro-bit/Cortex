# Presentation Contract

The presentation layer converts Cortex review workflow state into read-only
view models. It is the bridge between the bounded review workflow and a future
UI, CLI preview, or demo screen.

It is not a UI and not a reasoning layer.

## Core Rule

Presentation may arrange review state for display. It may not create, confirm,
reject, resolve, or mutate investigative state.

Presentation should stay boring: plain, deterministic, inspectable, low-magic,
and easy to test. If presentation becomes clever, it risks becoming a hidden
reasoning layer.

## View Models

`WorkflowStageView`
: Shows where a record sits in the review path. A stage status is display
state only.

`ClaimReviewCardView`
: Shows claim review status, support counts, contradiction counts, uncertainty
counts, provenance ids, lineage ids, priority, and warnings. It does not alter
claim matrix confidence.

`SourceReviewCardView`
: Shows source-review risk, reliability, evidence counts, provenance ids,
lineage ids, contamination flags, and warnings. It does not accept or reject a
source.

`SessionTimelineView`
: Shows session and audit events. Audit timeline entries are workflow history,
not evidence.

`BundlePreviewView`
: Shows review bundle sections and limitations. It is not a final report.

`ReviewDashboardView`
: Groups stage, claim, source, session, bundle, unresolved, deferred,
contradiction, uncertainty, provenance, warning, and limitation views.

`DemoPresentation`
: A synthetic-only presentation fixture for future UI work.

Future view models may include `ProvenanceReferenceView`,
`UncertaintyPanelView`, or `ContradictionPanelView` if provenance,
uncertainty, or contradiction display logic begins repeating. Until then,
keeping these as explicit fields is simpler.

## Required Visibility

Presentation output should preserve:

- unsupported claim labels
- source risk as warning, not rejection
- contradictions
- deferred items
- unresolved items
- uncertainty notes
- provenance references
- limitations
- synthetic demo labels
- audit-as-workflow-history warnings
- visibly missing provenance, unknown fields, missing dates, and not-supplied
  values

## Forbidden Behavior

Presentation must not:

- create evidence
- create claims
- create graph edges
- create review decisions
- change claim confidence
- change source trust
- hide contradictions
- hide provenance gaps
- remove synthetic labels
- turn review bundles into final reports
- aggregate warnings, grouped cards, or dashboard counts into stronger truth
  signals
- normalize unknown or missing values into neat display values that imply they
  were reviewed, harmless, or supplied

## No Aggregation Semantics

Presentation grouping must not imply stronger meaning.

Examples:

- Three warnings shown together do not become stronger evidence.
- Multiple claim cards grouped by topic do not imply corroboration.
- Multiple source cards in one panel do not imply independence.
- A dashboard count is display metadata, not evidentiary weight.

Grouping is for visual organization only.

## Absent Data

Absent data should remain visibly absent.

- Missing provenance remains missing.
- Unknown source fields remain unknown.
- Missing dates remain missing.
- Empty panels should show missing, unknown, or not supplied state rather than
  silently disappearing.
- `N/A` must not imply reviewed, harmless, or resolved.

## Future UI Guidance

A future UI should consume `DemoPresentation` first. It should render
`ReviewDashboardView` and its child views directly, without reconstructing
workflow logic in the frontend.

If the UI needs a new display shape, add it here as a view model before adding
screen code.
