# ADR-017: Claim Extraction Without Confirmation

## Status

Accepted.

## Context

After observation classification, the framework can distinguish direct
observation, interpretation, speculation, reported claims, metadata statements,
and unknown spans. The next risk is treating claim extraction itself as evidence
support.

Extracting "this text contains a claim" must not become "this claim is true" or
"this claim is supported."

## Decision

Add deterministic candidate claim extraction:

- `CandidateClaim`
- `CandidateClaimOrigin`
- `ClaimExtractionResult`
- `ClaimExtractionWarning`
- `ClaimExtractionPolicy`
- `ClaimExtractionEngine`

Candidate claims start with:

- `status = unsupported`
- `confidence = 0.0`
- source observation id when available
- source evidence id when available
- provenance ids when available
- extraction warnings

## Origins

Candidate claim origins preserve where the claim-like statement came from:

- `from_direct_observation`
- `from_reported_claim`
- `from_interpretation`
- `from_speculation`
- `from_metadata`
- `unknown`

## Guardrails

Claim extraction does not:

- create graph edges
- create support relationships
- add claim confidence
- confirm claims
- mutate evidence
- treat speculation as fact
- treat reported claims as verified observations

## Consequences

The claim matrix can later receive cleaner candidate inputs, but support and
contradiction remain separate operations. Future LLM extraction should conform
to the same boundary before it is trusted as a framework component.
