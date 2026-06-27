# Current State

Last verified: 2026-06-27

This document is a reorientation snapshot for Roswell UAP Cortex after the
evidence-quality and review-integration phases. It is not a roadmap, product claim, validation report, or assurance case.

## Health Check

Latest local verification:

```powershell
python -m pytest
```

Result:

- `393 passed`

## What Cortex Can Do Now

Cortex can run a deterministic synthetic review pipeline:

```text
raw input
-> ingestion / normalization
-> evidence / provenance / lineage
-> evidence quality assessment
-> candidate claim extraction
-> claim normalization
-> claim evidence evaluation
-> evidence-quality-aware review packaging
-> claim and source review dockets
-> working memory / review sessions
-> audit trail / review bundles
-> bounded retrieval, reasoning, discourse, persistence, and evaluation
```

It can preserve:

- provenance
- source lineage
- contamination warnings
- observation vs interpretation boundaries
- unsupported claim state
- possible support vs possible contradiction
- evidence-quality dimensions
- review priority as attention only
- contradiction visibility
- uncertainty notes
- synthetic-evaluation limitations
- adversarial calibration limitations

## What Cortex Still Cannot Do

Cortex still does not:

- ingest real UAP data
- decide truth
- operate as a system that does not decide truth
- confirm claims automatically
- reject sources automatically
- operate as a production system
- provide operational, regulatory, safety, or certification guidance
- run real LLM inference
- call cloud APIs
- use a vector database
- act as an autonomous agent
- provide a web UI
- validate transferability to predictive maintenance or any other domain

## Strongest Current Foundation

The strongest parts of the framework are now:

- evidence/provenance/lineage separation
- claim extraction and normalization without confirmation
- claim/source review dockets
- evidence-quality rubric and quality-aware review packaging
- reality-boundary and recursive-inference protection
- adversarial smoke tests, hard tests, calibration baselines, and documented
  limitations
- documentation discipline around what scores and labels must not mean

## Current Risk Areas

The main watchpoints are:

- `README.md` is still readable but increasingly dense.
- `models.py` remains broad by design; defer splitting until a real ownership
  problem appears.
- Review workflow objects are numerous and should not duplicate each other.
- Evidence quality must remain record condition, not truth confidence.
- Review bundles now preserve evidence-quality summaries, but their quality
  sections must remain review context rather than findings.
- Future UI work must consume presentation/review models without inventing
  hidden reasoning or aggregation semantics.
- Transferability remains deferred until more synthetic evidence and boundary
  testing exist.

## Best Next Phase Candidates

Recommended next phase:

**Phase 30: Review Bundle Quality Guardrail Expansion Or README Scope Reorganization**

Reason:
Evidence quality now flows through review dockets and bundles. The next narrow
step is either to expand bundle-specific adversarial tests or to reorganize the
README current-scope ledger into clearer sections before the next feature.

Other reasonable candidates:

- review bundle quality guardrail expansion
- README scope reorganization
- hard-adversarial remediation for known near misses
- current roadmap refresh
- UI-readiness view-model audit

## Reorientation Rule

Before the next major expansion, keep this boundary:

> Cortex may improve visibility, ordering, review context, and uncertainty
> preservation. It must not convert those improvements into truth, authority,
> safety, certification, or operational validity.
