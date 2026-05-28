# Roswell UAP Cortex

A cognitive investigative assistant framework for uncertain evidence domains.

This project does not claim truth. Its purpose is to preserve uncertainty while
organizing evidence, claims, memory, contradictions, timelines, graph context,
and source trust.

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
- An AI debt register documenting future risks around inference, provenance,
  semantic similarity, temporal parsing, scoring, evaluation, and reporting.
- Tests proving memory, source-trust, timeline, graph, claim-matrix,
  associative retrieval, ingestion, bounded reasoning, discourse, and
  persistence behavior.

## Project Layout

```text
Roswell-uap-cortex/
  docs/
    AI_DEBT.md
    MEMORY_MODEL.md
    PROBLEM_STATEMENT.md
  src/
    roswell_uap_cortex/
      __init__.py
      associative.py
      claim_matrix.py
      citations.py
      cli.py
      context_builder.py
      correlation_guard.py
      discourse.py
      discourse_guardrails.py
      graph.py
      guardrails.py
      independence.py
      ingestion.py
      llm_adapter.py
      models.py
      mock_reasoner.py
      memory.py
      narrative.py
      persistence.py
      persistence_guardrails.py
      provenance.py
      reasoning.py
      serialization.py
      snapshot.py
      snapshot_validator.py
      text.py
      timeline.py
      uncertainty.py
  tests/
    test_memory_merge.py
    test_phase2_evidence_trust.py
    test_phase3_investigative_graph.py
    test_phase4_associative_retrieval.py
    test_phase5_ingestion.py
    test_phase6_reasoning.py
    test_phase7_discourse.py
    test_phase8_persistence.py
  pyproject.toml
  README.md
```

## Development

Install test dependencies and run the suite:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Design Principle

The system should help investigators ask better questions, notice uncertainty,
surface contradictions, and retain provenance. It should not present uncertain
claims as established fact.
