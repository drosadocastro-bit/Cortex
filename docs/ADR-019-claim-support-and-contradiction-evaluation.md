# ADR-019: Claim Support And Contradiction Evaluation

Status: Accepted

## Context

Earlier phases can ingest raw text, classify observations, extract candidate
claims, normalize those claims, and register unsupported claim topics. The next
gap is controlled comparison between normalized claims and evidence records.

That comparison must remain bounded. It can identify possible support,
possible contradiction, uncertainty, irrelevance, or review pressure, but it
must not decide truth or mutate the claim graph.

## Decision

Phase 17 adds `ClaimEvidenceEvaluator`, `ClaimContradictionEvaluator`, and
`ClaimEvidenceGuardrails`.

The evaluator compares `NormalizedClaim` records with `EvidenceItem` records
using deterministic lexical overlap, observation classification metadata,
provenance visibility, lineage visibility, and contradiction markers.

The output is a `ClaimEvaluationResult` containing assessment records,
support signals, contradiction signals, uncertainty signals, and warnings.

Assessment labels are deliberately cautious:

- `possible_support`
- `possible_contradiction`
- `uncertain`
- `irrelevant`
- `needs_review`

The claim matrix can consume these assessments, but only as bounded support or
contradiction contributions. Same-lineage repetition is downgraded and
duplicate lineage no longer receives a confidence bonus.

## Why Support Is Not Confirmation

Evidence can appear to support a normalized claim without proving it. A
matching phrase may be copied, paraphrased, speculative, reported, derivative,
or missing provenance. For this reason, support signals do not set truth and do
not mutate the source claim. They are review inputs.

## Why Contradiction Is Not Disproof

Contradiction pressure can indicate that records disagree, contain negation, or
carry mutually exclusive terms. It does not prove that either side is false.
Contradictions are preserved because unresolved conflict is useful
investigative state.

## Why Observation Type Matters

Direct observation, reported claim, speculation, metadata, and unknown spans
should not contribute equally. Metadata does not become event truth,
speculation is capped, and reported claims stay visibly cautious.

## Why Same-Lineage Repetition Is Downgraded

Repeated paraphrases from the same lineage are not independent corroboration.
The evaluator marks same-lineage evidence, and the claim matrix groups repeated
lineage before scoring. This prevents copied evidence from creating artificial
confidence.

## Consequences

Positive:

- Normalized claims can now be reviewed against evidence without confirmation.
- Support and contradiction signals remain separate.
- Mixed support and contradiction pressure is labeled `needs_review`.
- Missing provenance and weak observation types remain visible.

Tradeoffs:

- The contradiction detector is intentionally simple and conservative.
- Lexical matching may miss subtle contradictions.
- Future semantic or LLM-assisted evaluators must preserve the same output
  shape and guardrails before replacing deterministic rules.

## Non-Goals

- No truth decisions.
- No automatic support graph edges.
- No LLM calls.
- No vector database use.
- No ingestion of real UAP data.
