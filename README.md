# Roswell UAP Cortex

An experimental cognitive framework and epistemic research sandbox for uncertain,
noisy, unstructured evidence domains.

**Disclaimer:** This is a personal, independent hobby project conducted entirely on personal time, personal equipment, and personal resources. The views, logic architectures, design patterns, documentation, and code expressed in this repository are solely those of the author and do not represent the official policy, position, endorsement, or technical guidance of the Federal Aviation Administration (FAA), the Department of Transportation (DOT), or the United States Government.

This project is exploratory and educational in nature. It is **not intended for
operational analysis, automated truth determination, or production deployment**.
It is a testbed for uncertainty-preserving extraction and reasoning - a
cognitive architecture experiment rather than a finished system.

The framework attempts to model brain-inspired mechanisms such as memory,
associative activation, contradiction handling, temporal ordering, and bounded
reasoning. It is intended to explore how these mechanisms interact when applied
to noisy, incomplete, and contested real-world evidence, not to produce
authoritative conclusions.

This project does not claim truth. Its purpose is to preserve uncertainty while
organizing evidence, claims, memory, contradictions, timelines, graph context,
and source trust - retaining provenance, lineage, contamination risk, and
epistemic tension throughout.

The framework is intentionally skeletal at this stage:

- No UI.
- No real UAP data ingestion.
- No LLM calls.
- No truth assertions.
- Vector search is treated as secondary to graph, timeline, and source-trust reasoning.

## Table Of Contents

- [Current Scope](#current-scope)
  - [Core Evidence And Memory](#core-evidence-and-memory)
  - [Ingestion And Provenance](#ingestion-and-provenance)
  - [Claims, Quality, And Review](#claims-quality-and-review)
  - [Reasoning, Retrieval, And Discourse](#reasoning-retrieval-and-discourse)
  - [Persistence, Evaluation, And Safety](#persistence-evaluation-and-safety)
  - [Navigation Notes](#navigation-notes)
- [Project Layout](#project-layout)
- [Development](#development)
- [Research Roadmap](#research-roadmap)
- [Design Principle](#design-principle)
- [Understanding The Code](#understanding-the-code)

## Current Scope

The framework is organized around an evidence-first review path. The sections
below summarize what exists today; deeper ownership maps live in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md),
[`docs/WORKFLOW_MAP.md`](docs/WORKFLOW_MAP.md), and
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

### Core Evidence And Memory

- Domain dataclasses for evidence, claims, source trust, memory records, graph
  nodes, timelines, contradictions, and review artifacts.
- Memory decay and duplicate memory merging, so repeated observations can
  reinforce stable records without accumulating redundant copies.
- Source trust, source independence, lineage, contamination, and corroboration
  helpers that preserve caution without automatic conclusions.
- Graph relationship models and deterministic graph backends for entities,
  events, sources, claims, evidence, contradiction lookup, lineage paths, and
  temporal links.
- Timeline memory that orders exact dates while preserving approximate,
  partial, fuzzy, and unknown dates without fabricating precision.

### Ingestion And Provenance

- Deterministic ingestion that normalizes raw inputs into evidence,
  observations, provenance, lineage, contamination flags, and ingestion
  warnings.
- Observation classification that keeps direct observations, interpretations,
  speculation, reported claims, metadata statements, and unknown spans
  separated at intake.
- Sensory-intake safeguards: ingestion does not confirm claims, rank claims,
  create graph edges, or create support relationships automatically.
- Provenance and lineage travel with records so derivative sources, repeated
  source URIs, missing fields, and weak chain-of-custody remain visible.

### Claims, Quality, And Review

- Candidate claim extraction, claim normalization, and claim matrix integration
  that keep extracted and normalized claims unsupported with zero confidence
  until reviewed.
- Claim evidence evaluation that emits possible support, possible
  contradiction, uncertainty, irrelevance, and needs-review signals without
  confirming or disproving claims.
- Evidence quality assessment across provenance completeness, lineage clarity,
  source transparency, observation directness, contamination resistance,
  contradiction stability, temporal specificity, and extraction confidence.
- Claim and source review dockets that include evidence assessments,
  evidence-quality summaries, provenance, lineage, uncertainty, warnings, and
  recommendations for human inspection.
- Review priority, working memory, review sessions, audit trails, and review
  bundles that organize review state without mutating evidence, confirming
  claims, accepting or rejecting sources, or creating graph edges.
- Review bundle exports that preserve evidence-quality summaries,
  unresolved items, uncertainty, provenance, audit trails, limitations, and
  quality boundaries without becoming final reports.

### Reasoning, Retrieval, And Discourse

- Associative activation and correlation guarding that retrieve possible,
  weak, and contested associations without creating confirmation.
- Controlled semantic and hybrid retrieval layers with deterministic mock
  embeddings, component scores, semantic warnings, and future vector-ready
  abstractions.
- Attention and salience gating that ranks review priority while preserving
  noisy evidence warnings, contradiction pressure, provenance gaps, and
  same-lineage suppression.
- Bounded local reasoning over activated context with deterministic mock
  reasoning, context-window trimming, speculative labeling, and guardrails that
  prevent mutation of evidence, claims, or graph structures.
- Investigative discourse, citations, uncertainty formatting, and deterministic
  narrative separation for observations, interpretations, speculation, and
  unresolved uncertainty.

### Persistence, Evaluation, And Safety

- Snapshot persistence with manifests, schema versioning, record counts,
  deterministic checksums, unknown-field preservation, and guarded local JSON
  save/load behavior.
- Session persistence and audit trails that save workflow history without
  applying review decisions to evidence, claims, sources, graph records, or
  truth state.
- Synthetic evaluation harnesses, scenario datasets, epistemic metrics, and
  deterministic reports with mandatory limitations.
- Reality-boundary and live-inference safety layers that keep evidence, claims,
  reasoning outputs, discourse outputs, semantic clusters, retrieval results,
  speculative hypotheses, synthetic evaluations, and external input separated.
- Adversarial smoke tests, OWASP-inspired hard scenarios, calibration
  baselines, error-taxonomy reporting, remediation notes, and an AI debt
  register that keep known limitations visible.

### Navigation Notes

- Start with [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) for the latest
  reorientation snapshot and next-phase candidates.
- Use [`docs/WORKFLOW_MAP.md`](docs/WORKFLOW_MAP.md) to understand review
  workflow ownership and sprawl boundaries.
- Use [`docs/API_AND_MODEL_MAP.md`](docs/API_AND_MODEL_MAP.md) before larger
  refactors or public API changes.
- Use [`docs/ADVERSARIAL_RESULTS_GUIDE.md`](docs/ADVERSARIAL_RESULTS_GUIDE.md)
  to interpret adversarial smoke, hard, and calibration results.
- Use [`docs/AI_DEBT.md`](docs/AI_DEBT.md) to check future-risk watchpoints
  before adding AI, vector, UI, connector, or transferability features.
## Project Layout

```text
Roswell-uap-cortex/
  docs/
    AI_DEBT.md
    API_AND_MODEL_MAP.md
    ADR-029-adversarial-calibration-expansion.md
    ADR-030-evidence-quality-rubric.md
    ADR-031-evidence-quality-review-integration.md
    ADR-032-review-bundle-quality-integration.md
    ADVERSARIAL_CALIBRATION_BASELINE.md
    ADVERSARIAL_FINDINGS.md
    ADVERSARIAL_RESULTS_GUIDE.md
    ARCHITECTURE.md
    CODE_WALKTHROUGH.md
    CURRENT_STATE.md
    DEMO_WORKSPACE.md
    DEBUGGING_AND_SECURITY.md
    GOVERNANCE.md
    HARD_ADVERSARIAL_FINDINGS.md
    HARD_ADVERSARIAL_REMEDIATION.md
    MAINTENANCE_LOG.md
    MEMORY_MODEL.md
    PHASE_18_2_CONSOLIDATION.md
    PHASE_23_2_CONSOLIDATION.md
    PHASE_25_2_CONSOLIDATION.md
    PHASE_26_4_ADVERSARIAL_CONSOLIDATION.md
    PHASE_27_1_EVIDENCE_QUALITY_HYGIENE.md
    PHASE_30_DOCUMENTATION_NAVIGATION.md
    PRESENTATION_CONTRACT.md
    PROBLEM_STATEMENT.md
    PUBLIC_API.md
    REVIEW_REASONING_BOUNDARY.md
    SYNTHETIC_SCENARIO_DATASET.md
    UI_READINESS_NOTES.md
    WORKFLOW_MAP.md
  src/
    roswell_uap_cortex/
      __init__.py
      associative.py
      adversarial.py
      adversarial_report.py
      adversarial_scenarios.py
      artifact_registry.py
      attention.py
      attention_gate.py
      attention_guardrails.py
      claim_contradiction_evaluator.py
      claim_evaluation.py
      claim_evaluation_guardrails.py
      claim_matrix.py
      claim_extraction.py
      claim_matrix_integration.py
      claim_normalization.py
      claim_normalization_guardrails.py
      claim_review.py
      citations.py
      cli.py
      context_builder.py
      correlation_guard.py
      discourse.py
      discourse_guardrails.py
      demo_presentation.py
      demo_workspace.py
      demo_workspace_guardrails.py
      evidence_docket.py
      evidence_quality.py
      evidence_quality_guardrails.py
      evaluation.py
      evaluation_guardrails.py
      evaluation_report.py
      embedding_backend.py
      graph.py
      graph_backend.py
      guardrails.py
      hard_adversarial.py
      hard_adversarial_report.py
      hard_adversarial_scenarios.py
      hybrid_retrieval.py
      independence.py
      ingestion.py
      inference_provenance.py
      focus.py
      llm_adapter.py
      live_inference_guardrails.py
      models.py
      mock_reasoner.py
      memory.py
      metrics.py
      narrative.py
      networkx_backend.py
      observation_classifier.py
      persistence.py
      persistence_guardrails.py
      presentation.py
      presentation_guardrails.py
      provenance.py
      reasoning.py
      reality_boundary.py
      recursive_guard.py
      review_bundle.py
      review_bundle_formatter.py
      review_bundle_guardrails.py
      review_context.py
      review_influence.py
      review_priority.py
      review_session.py
      salience_policy.py
      scenario_dataset.py
      semantic.py
      semantic_clustering.py
      semantic_guardrails.py
      serialization.py
      scenarios.py
      session_audit.py
      session_audit_formatter.py
      session_formatter.py
      session_persistence.py
      snapshot.py
      snapshot_validator.py
      source_risk.py
      source_review.py
      source_review_formatter.py
      temporal.py
      text.py
      timeline.py
      uncertainty.py
      working_memory.py
  tests/
    test_memory_merge.py
    test_phase2_evidence_trust.py
    test_phase3_investigative_graph.py
    test_phase4_associative_retrieval.py
    test_phase5_ingestion.py
    test_phase6_reasoning.py
    test_phase7_discourse.py
    test_phase8_persistence.py
    test_phase8_1_evaluation.py
    test_phase9_graph_temporal.py
    test_phase10_semantic.py
    test_phase11_reality_boundary.py
    test_phase12_attention.py
    test_phase13_1_hard_adversarial.py
    test_phase13_2_hygiene.py
    test_phase13_adversarial.py
    test_phase14_observation_classification.py
    test_phase15_claim_extraction.py
    test_phase16_claim_normalization.py
    test_phase17_claim_evaluation.py
    test_phase18_2_consolidation.py
    test_phase18_claim_review.py
    test_phase19_source_review.py
    test_phase20_working_memory.py
    test_phase21_session_persistence.py
    test_phase22_review_bundle.py
    test_phase23_demo_workspace.py
    test_phase23_2_consolidation.py
    test_phase23_3_workflow_map.py
    test_phase24_boundary_docs.py
    test_phase24_review_reasoning_boundary.py
    test_phase25_2_consolidation.py
    test_phase25_3_api_model_map.py
    test_phase25_presentation_contract.py
    test_phase26_scenario_expansion.py
    test_phase27_evidence_quality.py
    test_phase27_1_evidence_quality_hygiene.py
    test_phase28_quality_review_integration.py
    test_phase29_review_bundle_quality.py
    test_phase30_readme_navigation.py
  pyproject.toml
  README.md
```

## Development

Install test dependencies and run the suite:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Research Roadmap

See [`docs/RESEARCH_ROADMAP.md`](docs/RESEARCH_ROADMAP.md) for the next planned
experiments: observation vs interpretation separation, lineage and repeated-source
bias, associative activation, contradiction-preserving discourse, and memory
formation and decay.

## Design Principle

The system should help investigators ask better questions, notice uncertainty,
surface contradictions, and retain provenance. It should not present uncertain
claims as established fact.

## Understanding The Code

See [`docs/CODE_WALKTHROUGH.md`](docs/CODE_WALKTHROUGH.md) for a maintainer
walkthrough of how the modules work together.

See [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) for the latest
reorientation snapshot, current boundaries, and strongest next phase
candidates.

See [`docs/WORKFLOW_MAP.md`](docs/WORKFLOW_MAP.md) for the review workflow map
that separates cognitive core, review workflow, session/audit, export/demo, and
evaluation responsibilities.

See [`docs/API_AND_MODEL_MAP.md`](docs/API_AND_MODEL_MAP.md) for the current
public surface and model ownership map before larger refactors.

See [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) for the recurring rule that every
five major phases should pause feature expansion for architecture
consolidation, debugging, and security hygiene.


