# ADR-020: Claim Review Workflow

Status: Accepted

## Context

The framework can now ingest evidence, classify observations, extract candidate
claims, normalize them, and evaluate possible support or contradiction. Those
signals are useful only if they remain reviewable without becoming conclusions.

Phase 18 adds a deterministic review workflow that packages claim assessments
into dockets for human inspection.

## Decision

Add `ClaimReviewEngine`, `ReviewPriorityEngine`, and
`EvidenceDocketFormatter`.

The review workflow produces `ClaimReviewDocket` records containing
`ClaimReviewItem` entries, evidence assessment summaries, citations, warnings,
and cautious recommendations.

Review priority considers:

- contradiction visibility
- simultaneous support and contradiction pressure
- missing provenance
- same-lineage repetition
- speculative or reported evidence
- low independence
- uncertainty signals

Priority is review priority only. It is not truth confidence, operational
urgency, or evidence validity.

## Why This Layer Exists

Claim evaluation produces signals. Human review needs those signals arranged
without flattening them into a single answer. The docket layer gives Cortex a
stable bridge between internal assessment and future UI or reporting work.

## Why Recommendations Stay Bounded

Recommendations describe next review actions such as checking provenance,
reviewing contradiction pressure, or inspecting source independence. They do
not confirm claims, reject claims, create graph edges, or mutate evidence.

## Why Dockets Are Separate From Discourse

Discourse presents broader reasoning context. Claim review dockets are narrower:
they focus on one or more normalized claims and the evidence assessments
attached to them. This keeps the claim-review workflow explicit and testable.

## Consequences

Positive:

- Claims that need attention can be prioritized deterministically.
- Support and contradiction remain separate in the review package.
- Provenance, lineage, uncertainty, and same-lineage warnings stay visible.
- Future UI work can render dockets without inventing claim semantics.

Tradeoffs:

- Priority scoring is heuristic and intentionally conservative.
- Dockets do not replace full discourse, graph exploration, or source analysis.
- Future real data may require richer review categories, but they must preserve
  the same epistemic boundaries.

## Non-Goals

- No UI.
- No claim confirmation.
- No claim rejection.
- No graph edge creation.
- No LLM or API calls.
- No autonomous review agent.
