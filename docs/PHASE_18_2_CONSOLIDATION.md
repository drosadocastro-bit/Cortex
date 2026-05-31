# Phase 18.2 Consolidation Report

Date: 2026-05-31

## Scope

This pass pauses feature growth after Phases 14 through 18. The goal is to
verify that the claim pipeline remains understandable, deterministic,
provenance-aware, and bounded.

Reviewed path:

```text
ingestion
-> observation classification
-> candidate claim extraction
-> claim normalization
-> claim evidence evaluation
-> claim review dockets
```

## Findings

Architecture:

- The Phase 14-18 claim pipeline fits the canonical flow.
- Each layer has a distinct purpose:
  - classification labels observation type
  - extraction creates unsupported candidate claims
  - normalization groups candidate claims without validation
  - evaluation compares claims and evidence without truth decisions
  - review dockets package signals for human inspection
- No new layer needs to become a reasoning engine, graph writer, or truth
  resolver.

Debugging:

- Focused claim-pipeline tests passed.
- The new consolidation test verifies the ordered pipeline does not mutate
  evidence, does not create graph edges, and preserves unsupported claim state.
- The documentation map needed one exact class-name reference for
  `ObservationClassifier`; this was corrected in `CODE_WALKTHROUGH.md`.

Security and safety hygiene:

- The Phase 14-18 modules contain no local matches for network clients,
  subprocess execution, dynamic execution, unsafe pickle use, or unsafe YAML
  loading patterns checked by the hygiene test.
- No new dependency was added.
- No LLM, API, vector database, or autonomous workflow was introduced.

Public API:

- The broad package export surface remains intentionally transitional.
- Phase 18 review classes are exported because tests and documentation treat
  the review workflow as part of the canonical path.
- Future cleanup should still split core, extension, experimental, and testing
  namespaces deliberately.

## Fixes

- Added `tests/test_phase18_2_consolidation.py`.
- Updated `CODE_WALKTHROUGH.md` to name `ObservationClassifier` explicitly.
- Added this consolidation report.
- Updated maintenance and hygiene documentation for the Phase 14-18 checkpoint.

## Verification

Commands run:

```powershell
rg -n "import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system" src tests
rg -n "openai|chromadb|sentence-transformers|qdrant|pinecone|weaviate|requests|httpx" pyproject.toml src tests
python -m pytest tests\test_phase13_2_hygiene.py tests\test_phase14_observation_classification.py tests\test_phase15_claim_extraction.py tests\test_phase16_claim_normalization.py tests\test_phase17_claim_evaluation.py tests\test_phase18_claim_review.py
python -m pytest tests\test_phase18_2_consolidation.py
python -m pytest
```

Expected benign scan hits:

- The broad regex appears inside hygiene tests because the tests define the
  forbidden-pattern expression.
- Dependency-name strings appear inside tests that assert those packages are
  absent from `pyproject.toml`.

## Remaining Debt

- `__init__.py` remains broad. This is documented and accepted during the
  research phase, but future namespace cleanup should be deliberate.
- The claim evaluator is lexical and rule-based. It is intentionally limited
  until semantic or local-inference comparison can be added behind the same
  guardrails.
- Review priority is a heuristic review signal. It must not be displayed as
  truth confidence in any future UI or report.
