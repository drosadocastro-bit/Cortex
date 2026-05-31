# Maintenance Log

## 2026-05-30: Phase 17 Claim Support And Contradiction Evaluation

Scope:
Compare normalized claims with evidence records as bounded review signals while
preserving the rule that support is not confirmation and contradiction is not
disproof.

Fixes / documentation added:

- Added `ClaimEvidenceEvaluator`, `ClaimContradictionEvaluator`, and
  `ClaimEvidenceGuardrails`.
- Added claim assessment, support, contradiction, uncertainty, policy, and
  warning models.
- Added `ClaimMatrixEngine.register_evidence_assessments()` for conservative
  matrix integration of possible support and contradiction signals.
- Removed duplicate same-lineage confidence bonus from claim matrix scoring.
- Added `docs/ADR-019-claim-support-and-contradiction-evaluation.md`.
- Updated architecture, memory model, code walkthrough, README, and AI debt
  docs.

Verification:

- `python -m pytest`

## 2026-05-29: Phase 13.2 Architecture, Debugging, And Security Hygiene

Scope:
Architecture consolidation, public API discipline, local debugging checks,
dependency-surface review, and documentation of findings.

Findings:

- The canonical architecture needed one concise map after rapid phase growth.
- `__init__.py` exports are broad and convenient, but the public API is not yet
  disciplined.
- Source and tests did not show obvious network, process execution, dynamic
  execution, pickle, or unsafe YAML-loading patterns in the local regex scan.
- README/docs did not show the checked mojibake markers in the local regex scan.
- The global Python environment contains many unrelated packages; project
  dependency review should rely on `pyproject.toml`.
- Persistence loading uses JSON reconstruction and guardrail validation rather
  than executing loaded data.

Fixes / documentation added:

- Added `docs/ARCHITECTURE.md`.
- Added `docs/PUBLIC_API.md`.
- Added `docs/DEBUGGING_AND_SECURITY.md`.
- Added this maintenance log.
- Added hygiene tests for dependency surface, forbidden code patterns,
  documentation encoding markers, public import smoke behavior, and persistence
  no-execution behavior.

Verification:

- `python -m pytest`

## 2026-05-30: Phase 16 Claim Normalization And Matrix Integration

Scope:
Group candidate claims under deterministic canonical keys and register them in
the claim matrix as unsupported candidate topics only.

Fixes / documentation added:

- Added `ClaimCanonicalKey`, `NormalizedClaim`, `ClaimNormalizationPolicy`,
  `ClaimNormalizationWarning`, `ClaimNormalizationResult`, and
  `ClaimMatrixIntegrationResult`.
- Added `ClaimNormalizer`, `ClaimNormalizationGuardrails`, and
  `ClaimMatrixIntegrator`.
- Added safe `ClaimMatrixEngine.register_unsupported_candidate_topic()`.
- Added `docs/ADR-018-claim-normalization-and-matrix-integration.md`.
- Updated hard adversarial coverage with a polished paraphrase flood scenario.

Verification:

- `python -m pytest`

## 2026-05-30: Phase 15 Claim Extraction Without Confirmation

Scope:
Add deterministic candidate claim extraction from classified observations while
preserving the rule that extraction is not confirmation.

Fixes / documentation added:

- Added `CandidateClaim`, `CandidateClaimOrigin`, `ClaimExtractionPolicy`,
  `ClaimExtractionWarning`, and `ClaimExtractionResult`.
- Added `ClaimExtractionEngine`.
- Added `docs/ADR-017-claim-extraction-without-confirmation.md`.
- Updated architecture, memory model, code walkthrough, and AI debt docs.

Verification:

- `python -m pytest`

## 2026-05-30: Phase 14 Observation And Interpretation Separation

Scope:
Add deterministic observation classification at ingestion so direct
observation, interpretation, speculation, reported claims, metadata statements,
and unknown spans remain distinct.

Fixes / documentation added:

- Added `ObservationType`.
- Added `ObservationClassifier`.
- Extended `ExtractedObservation` with classification markers and notes.
- Propagated classification metadata into ingested `EvidenceItem` records.
- Added `docs/ADR-016-observation-interpretation-separation.md`.
- Updated architecture, memory model, code walkthrough, and AI debt docs.

Verification:

- `python -m pytest`

Notes:

The broad public API remains in place for compatibility. Future cleanup should
split foundational, extension, experimental, and testing surfaces deliberately
rather than removing exports opportunistically.

## 2026-05-30: Governance And Code Walkthrough

Scope:
Document the recurring consolidation cadence and add a maintainer-oriented
walkthrough explaining what the code does.

Fixes / documentation added:

- Added `docs/GOVERNANCE.md`.
- Added `docs/CODE_WALKTHROUGH.md`.
- Linked the recurring consolidation rule from `docs/ARCHITECTURE.md`.
- Linked the walkthrough and governance docs from `README.md`.
- Replaced two README em dashes with ASCII hyphens for consistency with the
  repository's ASCII-first editing style.

Verification:

- `python -m pytest`
