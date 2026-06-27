# Workflow Map

Roswell UAP Cortex now has enough review, session, export, and demo objects
that the workflow needs its own map. This document explains how records move
through the system and which layer owns each responsibility.

The purpose is not to add another subsystem. The purpose is to prevent workflow
objects from duplicating each other or blurring epistemic boundaries.

For public exports and model ownership, see `docs/API_AND_MODEL_MAP.md`.

## Main Review Path

```text
raw input
-> ingestion / normalization
-> extracted observations
-> evidence quality assessment
-> candidate claims
-> normalized claims
-> claim evidence evaluation
-> evidence-quality-aware review packaging
-> claim review dockets
-> source reliability dockets
-> working memory
-> review session
-> audit trail
-> evidence-quality-aware review bundle
-> review influence hints
-> bounded reasoning / discourse visibility
-> synthetic demo / future UI display
```

This path is review-oriented. It organizes uncertainty for human inspection. It
does not decide truth, confirm claims, reject sources, or resolve
contradictions automatically.

## Layer Ownership

| Layer | Owns | Must Not Own |
| --- | --- | --- |
| Cognitive core | Evidence records, provenance, lineage, claims, graph state, timeline state, memory, associations, semantic comparison, reasoning boundaries | Human workflow decisions, exported report language, UI state |
| Review workflow | Claim dockets, source dockets, review priority, active focus, reviewed/deferred/unresolved workflow state | Evidence mutation, claim confirmation, source truth, graph edge creation |
| Session and audit | Review decisions, session deltas, audit records, deterministic session persistence | Investigative truth state, source acceptance/rejection, hidden mutation on load |
| Export and demo | Review bundles, Markdown-ready bounded packets, synthetic demo fixtures | Final reports, operational conclusions, real data validation, external truth claims |
| Evaluation and adversarial testing | Synthetic behavior checks, adversarial scenarios, metrics, limitations | Scientific validation, real-world claim validation, production safety certification |

## Module Boundaries

`claim_review.py`
: Builds claim review dockets from normalized claims and evidence assessments.
It owns claim review packaging, optional evidence-quality summaries, and
recommendations. It does not own source review, session decisions, or report
export.

`evidence_docket.py`
: Summarizes possible support, possible contradiction, uncertainty, and
irrelevance for review. It does not create evidence or decide claim status.

`evidence_quality.py`
: Scores evidence condition across provenance, lineage, source transparency,
observation directness, contamination, contradiction pressure, temporal
specificity, and extraction confidence. Quality is review context only.

`source_review.py`
: Builds source reliability dockets from evidence, provenance, lineage,
contamination, evidence-quality summaries, and trust signals. It does not reject
or certify sources.

`source_risk.py`
: Scores source-review risk signals for review priority. It is not a source
truth engine.

`review_priority.py`
: Orders claim review attention. It is an attention signal only.

`working_memory.py`
: Collects the currently reviewable state: dockets, activated context,
reasoning output, discourse output, contradictions, unresolved items, and
uncertainty notes. It is not long-term evidence storage.

`review_session.py`
: Records human review decisions and deterministic session deltas. Decisions
are workflow annotations only.

`session_audit.py`
: Records workflow events such as session start, resume, decision, and report
formatting. Audit records are not evidence.

`session_persistence.py`
: Saves and loads review session envelopes. Loading must not apply decisions to
claims, evidence, sources, or graph records.

`session_formatter.py` and `session_audit_formatter.py`
: Render session and audit state for review. Formatting must not add new facts.

`review_bundle.py`
: Composes session state, dockets, audit trail, provenance references,
contradictions, uncertainty, evidence-quality summaries, and limitations into a
bounded review packet. It does not create a final report.

`review_bundle_formatter.py`
: Formats a bundle into deterministic Markdown-ready text. It must preserve
limitations and avoid certainty inflation.

`review_bundle_guardrails.py`
: Checks bundle text for missing limitations, missing provenance, missing audit
trail, and certainty-inflating language.

`demo_workspace.py`
: Runs a tiny synthetic-only fixture through the canonical path. It exists for
testing, documentation, and future UI rendering. It is not a real
investigation.

`demo_workspace_guardrails.py`
: Verifies that the demo stays synthetic and bounded.

`presentation.py`
: Converts review workflow state into read-only view models for display. It
does not create evidence, decisions, graph edges, or reasoning outputs.

`presentation_guardrails.py`
: Checks presentation output for missing synthetic labels, missing limitations,
missing provenance, hidden contradictions, and certainty-inflating language.

`demo_presentation.py`
: Converts the synthetic demo workspace into `DemoPresentation`, the first
future UI fixture.

## Boundary Rules

- A docket is a review package, not a decision.
- A session decision is a workflow annotation, not a claim update.
- An audit event is workflow history, not evidence.
- A bundle is a bounded review packet, not a final report.
- A bundle quality section is review context, not a finding.
- A demo workspace is an architecture exercise, not validation against reality.
- Review priority is attention, not confidence.
- Evidence quality is record condition, not confirmation.
- Evidence-quality summaries may raise review pressure, not evidentiary weight.
- Source risk is review pressure, not source rejection.
- Repeated lineage remains repeated lineage even if it appears across dockets,
  sessions, bundles, or demo output.

## Future UI Contract

A future UI should display this workflow state rather than invent a parallel
workflow. The first UI layer should probably be a small view-model layer that
adapts existing dockets, sessions, audit trails, and bundles into screen-ready
objects.

Review influence is documented in `docs/REVIEW_REASONING_BOUNDARY.md`. Review
state may guide attention, context selection, and discourse visibility, but it
must not become evidence, confidence, source truth, or graph support.

Presentation is documented in `docs/PRESENTATION_CONTRACT.md`. View models may
arrange workflow state for display, but they must not become workflow,
reasoning, or truth state.

The UI should not:

- create new claim confirmation paths
- mutate graph or evidence records through review decisions
- hide contradictions or uncertainty notes
- convert bundles into final reports
- treat demo output as real-world evidence

## Sprawl Watchlist

The current review workflow is coherent, but these boundaries should be watched
closely:

- claim dockets vs evidence dockets
- working memory vs review session state
- session persistence vs general persistence snapshots
- review bundles vs discourse output
- demo workspace vs future UI fixtures

If a future phase adds a new workflow object, it should state whether the object
is cognitive core, review workflow, session/audit, export/demo, or evaluation.
If it cannot be placed clearly, the simpler choice is usually to extend an
existing object.
