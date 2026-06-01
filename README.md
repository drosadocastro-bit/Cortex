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

## Current Scope

The initial framework provides:

- Domain dataclasses for evidence, claims, source trust, memory records, graph nodes,
  and contradictions.
- A memory decay engine that weakens unused or low-confidence memories.
- Duplicate memory merging so repeated observations reinforce stable memories instead
  of accumulating redundant records.
- Source trust, lineage, contamination, and corroboration engines for epistemic
  caution without automatic conclusions.
- Graph relationship models and an in-memory relationship graph for entities,
  sources, claims, events, and contradictions.
- A deterministic timeline engine that orders exact dates while preserving
  approximate and unknown dates.
- A claim matrix that separates support from contradiction and keeps repeated
  lineage from inflating confidence.
- Source independence scoring so semantic repetition is not treated as
  corroboration.
- Associative activation that retrieves possible related memories, claims,
  evidence, and entities without confirming relationships.
- A correlation guard that downgrades low-independence, high-overlap, or
  contradiction-heavy associations.
- Weak and contested associations remain visible in activated context for
  review.
- A vector-ready retrieval design that keeps future embeddings secondary to
  provenance, independence, and contradiction state.
- A deterministic ingestion layer that normalizes raw inputs into evidence,
  observations, provenance, source lineage, contamination flags, and ingestion
  warnings.
- Observation-vs-interpretation separation at intake, preserving direct
  observations, interpretations, speculation, reported claims, metadata
  statements, and unknown spans.
- Candidate claim extraction that turns classified observations into
  unsupported review candidates without creating support, graph edges, or
  confirmation.
- Claim normalization and matrix integration that groups candidate claims under
  canonical topics while preserving origin, provenance, lineage, unsupported
  status, and zero confidence.
- Claim support and contradiction evaluation that compares normalized claims
  against evidence as bounded review signals without confirming or disproving
  claims.
- Evaluation guardrails that preserve the distinction between possible support,
  possible contradiction, uncertainty, irrelevance, and needs-review pressure.
- Claim review dockets that package normalized claims, evidence assessments,
  provenance, lineage, uncertainty, warnings, and bounded review
  recommendations for human inspection.
- Source reliability review dockets that expose provenance quality, lineage
  risk, contamination flags, trust inputs, repeated source usage, and bounded
  source-review recommendations without accepting or rejecting sources.
- Working memory and review session state for tracking active focus, reviewed
  items, deferred items, unresolved contradictions, uncertainty notes, and
  deterministic session deltas without mutating investigative records.
- Session persistence and audit trails that save review sessions, decisions,
  deferred items, unresolved state, and workflow events as deterministic local
  JSON without creating evidence, claims, source truth, or graph edges on load.
- Review bundle exports that compose sessions, claim dockets, source dockets,
  unresolved items, uncertainty, provenance, audit trails, and limitations into
  deterministic Markdown-ready review packets without creating final reports.
- A fully synthetic demo workspace that runs the canonical Cortex path from raw
  inputs through review bundle output without real UAP data.
- Review-to-reasoning boundary contracts that allow review workflow state to
  guide attention, context visibility, and discourse annotations without
  becoming evidence, claim confidence, source truth, or graph support.
- Read-only workflow view models and a synthetic demo presentation contract
  that prepare future UI work without adding UI or presentation-side reasoning.
- Sensory intake safeguards: ingestion does not confirm claims or create graph
  edges automatically.
- A bounded local cognitive reasoning layer that operates on activated context
  without mutating evidence, claims, or graph structures.
- Context-window construction that trims duplicate lineage and preserves
  contradiction visibility to mitigate lost-in-the-middle risk.
- Reasoning guardrails for speculative labeling, unsupported claims, missing
  provenance, same-lineage repetition, and fictional contamination warnings.
- A deterministic mock reasoner plus adapter interface for future Nemotron,
  LM Studio, Ollama, vLLM, OpenAI API, or VLM perception integrations.
- An investigative discourse layer that turns activated context and bounded
  reasoning into structured human-review sections.
- Deterministic narrative separation for observations, interpretations,
  speculation, and uncertainty.
- Provenance citations and discourse guardrails that keep uncertainty,
  contradictions, weak associations, and contamination warnings visible.
- A tiny CLI harness for deterministic terminal discourse output, with future
  web interface possibilities kept separate.
- Snapshot persistence with manifest, schema versioning, record counts,
  deterministic checksums, and guarded local JSON save/load behavior.
- Immutable persistence boundaries: loading records does not create evidence,
  claims, graph edges, or truth state automatically.
- A synthetic evaluation harness with epistemic metrics, deterministic reports,
  no-mutation checks, and mandatory limitations.
- Graph backend abstraction with NetworkX integration for deterministic
  traversal, contradiction lookup, lineage paths, subgraphs, and temporal links.
- Conservative temporal helpers using `python-dateutil` behind wrappers that
  preserve fuzzy-date uncertainty.
- Controlled semantic layer with embedding backend abstraction, deterministic
  mock embeddings, semantic warnings, possible-related clusters, and hybrid
  retrieval component scores.
- Reality boundary layer with cognitive artifact separation, inference
  provenance chains, recursive inference protection, self-citation detection,
  and live-inference safety guardrails.
- Attention and salience gating that ranks review priority across records,
  preserves noisy evidence warnings, suppresses same-lineage dominance, and
  mitigates context overload without creating truth claims.
- Adversarial epistemic stress testing with synthetic attacks for provenance
  laundering, semantic echo, discourse contamination, confidence inflation,
  contradiction suppression, speculation hardening, and policy abuse.
- OWASP-inspired hard adversarial testing with honest outcomes including
  resisted, near-miss, expected-failure, unexpected-failure, and inconclusive
  results.
- An AI debt register documenting future risks around inference, provenance,
  semantic similarity, temporal parsing, scoring, evaluation, and reporting.
- Tests proving memory, source-trust, timeline, graph, claim-matrix,
  associative retrieval, ingestion, bounded reasoning, discourse, and
  persistence/evaluation behavior.

## Project Layout

```text
Roswell-uap-cortex/
  docs/
    AI_DEBT.md
    ADVERSARIAL_FINDINGS.md
    ARCHITECTURE.md
    CODE_WALKTHROUGH.md
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
    PRESENTATION_CONTRACT.md
    PROBLEM_STATEMENT.md
    PUBLIC_API.md
    REVIEW_REASONING_BOUNDARY.md
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
    test_phase25_presentation_contract.py
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

See [`docs/WORKFLOW_MAP.md`](docs/WORKFLOW_MAP.md) for the review workflow map
that separates cognitive core, review workflow, session/audit, export/demo, and
evaluation responsibilities.

See [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) for the recurring rule that every
five major phases should pause feature expansion for architecture
consolidation, debugging, and security hygiene.
