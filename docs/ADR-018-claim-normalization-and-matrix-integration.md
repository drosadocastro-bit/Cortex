# ADR-018: Claim Normalization And Matrix Integration

## Status

Accepted.

## Context

Candidate claims can now be extracted from classified observations. Without
normalization, repeated or paraphrased candidate claims would remain scattered
and hard to review. The risk is that grouping them could be mistaken for support
or corroboration.

## Decision

Add deterministic claim normalization and safe claim matrix integration:

- `ClaimNormalizer`
- `ClaimCanonicalKey`
- `NormalizedClaim`
- `ClaimNormalizationResult`
- `ClaimNormalizationWarning`
- `ClaimNormalizationPolicy`
- `ClaimMatrixIntegrator`
- `ClaimMatrixIntegrationResult`

Normalized claims are canonical groups of candidate claims. They preserve
candidate ids, evidence ids, provenance ids, lineage ids, and origin types.

## Why Normalization Is Not Validation

Normalization answers: "Do these candidate claims appear to be about the same
topic?"

It does not answer:

- whether the claim is true
- whether the claim is supported
- whether repeated phrasing is independent corroboration
- whether semantic similarity creates evidence

## Origin Preservation

Origin types remain visible. Speculation-origin claims remain speculative.
Reported claims remain reported. Metadata-origin claims cannot become event
truth. Cross-origin grouping is cautious and emits warnings when policy allows
it.

## Claim Matrix Integration

Normalized claims can be registered as unsupported candidate topics in the claim
matrix. Registration does not create supporting evidence, contradiction
evidence, graph edges, or confidence.

## Consequences

The claim matrix can now organize candidate topics before later support and
contradiction evaluation. This prepares the framework for future review flows
without collapsing organization into validation.
