# Problem Statement

Investigative domains with uncertain evidence are vulnerable to premature
conclusions, duplicate reports, source confusion, and narrative drift.

Roswell UAP Cortex is a framework skeleton for organizing uncertain evidence
without converting it into claims of truth. It is designed to help preserve the
distinction between:

- What was observed or recorded.
- Who or what reported it.
- Which claims are inferred from it.
- How confident the system is allowed to be.
- Where contradictions or unresolved alternatives remain.

## Goals

- Preserve uncertainty instead of collapsing it into certainty.
- Track sources and source trust separately from claim confidence.
- Distinguish primary evidence, secondary interpretation, speculation,
  contaminated repetition, and unsupported claims.
- Track evidence lineage so reposts and retellings are not counted as
  independent corroboration.
- Detect and represent contradictions explicitly.
- Merge duplicate memories rather than letting repeated copies distort recall.
- Apply memory decay so weak, unused records become less prominent over time.
- Reinforce repeated, consistent memories while retaining provenance.
- Keep vector search secondary to structured reasoning over graph links,
  timelines, source trust, and contradiction state.

## Non-Goals

- No UI in the initial skeleton.
- No ingestion of real UAP data.
- No LLM calls.
- No automated truth adjudication.
- No final claims about historical events.
- No automatic source-trust conclusions beyond deterministic caution scores.

## Operating Constraint

The framework may rank, group, compare, and qualify evidence. It must not claim
that contested or uncertain evidence is true merely because it appears multiple
times, is semantically similar, or comes from a persuasive narrative source.
