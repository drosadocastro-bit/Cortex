# ADR-026: Review-To-Reasoning Boundary

## Status

Accepted.

## Context

Cortex now has claim dockets, source review dockets, working memory, review
sessions, audit trails, bundles, and a synthetic demo workspace. These objects
help a human review uncertain evidence, but they also create a new risk:
workflow annotations could begin to look like evidence.

A reviewed claim must not become more true. A deferred item must not disappear.
A source-risk flag must not become source rejection. A bundle must not become a
reasoning input that changes claim confidence.

## Decision

Add a small review-to-reasoning boundary layer:

- `ReviewInfluencePolicy` converts review workflow state into bounded influence
  hints.
- `ReviewContextAdapter` carries those hints into activated context visibility
  without changing records.
- `ContextWindowBuilder` and `CognitiveReasoningEngine` may accept
  `ReviewInfluenceResult` as optional context-selection input.

Review influence is allowed to affect attention ordering, unresolved context,
deferred item visibility, provenance-gap visibility, source-review warning
visibility, and discourse annotations.

Review influence must not affect evidence records, claim matrix confidence,
source trust, graph edges, provenance records, or bundle and audit records as
evidence.

## Consequences

Human review state can shape what Cortex looks at next, but it cannot become
truth state. This preserves the analyst loop without creating hidden
confirmation channels.

The boundary also gives future UI work a safer contract: the UI can show review
influence, but it should not invent its own reasoning or mutation path.

## Non-Goals

- No UI is added.
- No LLM or API calls are added.
- No autonomous analyst behavior is added.
- No graph, claim, evidence, or source-trust mutation is performed.

## Guardrails

- Review priority is not confidence.
- Reviewed is not confirmed.
- Deferred is not erased.
- Source risk is not rejection.
- Audit is not evidence.
- Bundle text is not reasoning input.
- Review state is annotation state only.
