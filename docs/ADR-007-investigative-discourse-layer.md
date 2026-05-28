# ADR-007: Investigative Discourse Layer

## Status

Accepted.

## Context

The framework can ingest evidence, preserve provenance, activate focused
context, and produce bounded reasoning output. Human review still needs a
readable discourse layer that exposes what was observed, what is only
associated, what remains contradictory, and what is speculative.

Discourse must not become reasoning and narrative must not become evidence.

## Decision

Phase 7 adds deterministic investigative discourse:

- `DiscourseEngine` transforms `ReasoningOutput` and `ActivatedContext` into
  structured human-review sections.
- `CitationFormatter` creates deterministic citations from evidence,
  provenance, source, lineage, page, and timestamp data.
- `NarrativeBuilder` renders readable narrative while separating observations,
  interpretations, speculation, and uncertainty.
- `UncertaintyFormatter` summarizes unresolved contradictions, missing
  provenance, low-independence concerns, and speculative clusters.
- `DiscourseGuardrails` keeps provenance visible, preserves contradictions,
  labels speculation, and avoids certainty-inflating language.
- `cli.py` provides a tiny deterministic terminal harness for structured
  discourse output.

No web UI, vector database, real LLM inference, or autonomous agent behavior is
introduced.

## Rationale

### Discourse Is Separate From Reasoning

Reasoning produces structured cognitive output. Discourse presents that output
for human review. Keeping the layers separate prevents polished language from
being mistaken for evidence or confirmation.

### Narrative Generation Is Bounded

Narrative is built from deterministic templates and supplied structured fields.
It does not invent evidence, resolve contradictions, or upgrade possible
associations into support.

### Provenance Remains Visible

Every discourse response can carry citations tied to evidence, provenance,
source, and lineage. Claims should be reviewed through their evidence, not as
free-floating assertions.

### Uncertainty Is Exposed

The discourse layer explicitly includes weak associations, missing information,
reasoning warnings, uncertainty notes, and review-required status.

### Contradiction Visibility Is Mandatory

Contested context and contradiction warnings are preserved in their own section.
The system should not hide conflict to produce a cleaner narrative.

### Certainty Inflation Is Avoided

Discourse guardrails watch for certainty-inflating language and keep speculative
content labeled. The goal is explainable review, not authoritative conclusion.

## Consequences

The framework can now produce deterministic, bounded investigative discourse for
terminal review. A future web interface can render the same structured response
without changing the underlying epistemic rules.
