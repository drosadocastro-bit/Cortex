# Maintenance Log

## 2026-05-31: Phase 23 Synthetic Demo Workspace

Scope:
Add a fully synthetic demo workspace that exercises the canonical Cortex path
without real UAP data.

Fixes / documentation added:

- Added `DemoWorkspaceBuilder` and `DemoWorkspaceGuardrails`.
- Added demo workspace, manifest, and result models.
- Added a synthetic scenario with a primary-style note, contradiction,
  derivative repost, speculative contamination, and incomplete anonymous
  source.
- Added tests for deterministic build output, synthetic-only source ids,
  evidence/provenance/lineage production, candidate and normalized claims,
  claim/source dockets, session/audit/bundle output, contradiction and
  uncertainty coverage, contamination and derivative signals, guardrail
  rejection of non-synthetic sources, no graph-edge creation, and bundle
  formatting.
- Added `docs/ADR-025-synthetic-demo-workspace.md`.
- Added `docs/DEMO_WORKSPACE.md`.
- Updated architecture, memory model, code walkthrough, README, public API, and
  AI debt docs.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 22 Review Export And Report Bundles

Scope:
Compose sessions, claim dockets, source dockets, audit trails, unresolved
items, uncertainty, provenance, contradictions, and limitations into
deterministic Markdown-ready review packets.

Fixes / documentation added:

- Added `ReviewBundleBuilder`, `ReviewBundleFormatter`, and
  `ReviewBundleGuardrails`.
- Added review bundle, bundle section, bundle manifest, export result, and
  warning models.
- Added tests for deterministic bundle building, required sections, limitations,
  certainty-language guardrails, missing provenance warnings, no session/docket
  mutation, and no graph-edge creation.
- Added `docs/ADR-024-review-export-and-report-bundles.md`.
- Updated architecture, memory model, code walkthrough, README, public API, and
  AI debt docs.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 21 Session Persistence And Audit Trail

Scope:
Persist review sessions and audit trails while preserving the boundary that
session annotations are workflow records, not evidence or truth state.

Fixes / documentation added:

- Added `SessionAuditLogger`, `SessionPersistenceStore`, and
  `SessionAuditFormatter`.
- Added session audit record, audit trail, session persistence envelope, session
  save result, and session load result models.
- Added deterministic local JSON save/load with schema version, record counts,
  checksum, and limitations.
- Added tests for deterministic save/load, audit ordering, decision/deferred/
  unresolved round-trip, checksum detection, schema rejection, unknown-field
  preservation, formatter limitations, no graph mutation on load, and
  deterministic JSON output.
- Added `docs/ADR-023-session-persistence-and-audit-trail.md`.
- Updated architecture, memory model, code walkthrough, README, public API, AI
  debt, and debugging/security docs.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 20 Working Memory And Review Session State

Scope:
Add deterministic active review-session state that tracks focus, reviewed
items, deferred items, unresolved contradictions, uncertainty notes, and
session deltas without mutating investigative records.

Fixes / documentation added:

- Added `WorkingMemoryEngine`, `ReviewSessionEngine`, and `SessionFormatter`.
- Added review session, session state, review focus, reviewed item, deferred
  item, review decision, review decision type, and session delta models.
- Added tests for deterministic session starts, docket entry into working
  memory, reviewed/deferred tracking, unresolved contradiction visibility,
  uncertainty preservation, deterministic deltas, resume behavior, no claim or
  source truth promotion, formatter boundary language, and no graph/evidence
  mutation.
- Added `docs/ADR-022-working-memory-and-review-session-state.md`.
- Updated architecture, memory model, code walkthrough, README, public API, and
  AI debt docs.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 19 Source Reliability Review Layer

Scope:
Add deterministic source review dockets that summarize provenance, lineage,
contamination, trust inputs, source risk, and reliability signals without
accepting or rejecting sources.

Fixes / documentation added:

- Added `SourceReviewEngine`, `SourceRiskProfiler`, and
  `SourceReviewFormatter`.
- Added source review docket, item, reliability signal, risk signal,
  recommendation, and priority models.
- Added tests for source grouping, provenance gaps, derivative lineage,
  repeated source URI, contamination flags, speculative/reported content,
  source trust signals, claim/source boundary separation, no mutation,
  formatter language, and deterministic ordering.
- Added `docs/ADR-021-source-reliability-review-layer.md`.
- Updated architecture, memory model, code walkthrough, README, public API, and
  AI debt docs.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 18.2 Architecture, Debugging, And Security Hygiene II

Scope:
Consolidate the Phase 14-18 claim pipeline before adding more reasoning or
retrieval features.

Findings:

- The claim pipeline remains clear:
  observation classification -> candidate claim extraction -> claim
  normalization -> claim evidence evaluation -> claim review dockets.
- No Phase 14-18 module matched the checked network, process, dynamic
  execution, pickle, or unsafe YAML-loading patterns.
- No new dependency, LLM/API call, vector database, UI, or autonomous workflow
  was introduced.
- `__init__.py` remains broad; this is still a documented transitional API
  choice.

Fixes / documentation added:

- Added `tests/test_phase18_2_consolidation.py`.
- Added `docs/PHASE_18_2_CONSOLIDATION.md`.
- Updated `docs/DEBUGGING_AND_SECURITY.md` with the claim-pipeline hygiene
  check.
- Updated `docs/PUBLIC_API.md` to classify claim-pipeline and review exports.
- Updated `docs/CODE_WALKTHROUGH.md` to name `ObservationClassifier`
  explicitly.

Verification:

- `python -m pytest`

## 2026-05-31: Phase 18 Claim Review Workflow

Scope:
Package normalized claims and claim evaluation assessments into deterministic
review dockets for human inspection.

Fixes / documentation added:

- Added `ClaimReviewEngine`, `ReviewPriorityEngine`, and
  `EvidenceDocketFormatter`.
- Added claim review docket, review item, evidence assessment summary, queue,
  priority, and recommendation models.
- Added review tests for contradiction priority, unsupported claim preservation,
  separated support and contradiction, same-lineage warnings, provenance
  citations, missing provenance priority, speculative/reported labels,
  deterministic queue ordering, bounded formatter language, and no graph-edge
  creation.
- Added `docs/ADR-020-claim-review-workflow.md`.
- Updated architecture, memory model, code walkthrough, README, and AI debt
  docs.

Verification:

- `python -m pytest`

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
