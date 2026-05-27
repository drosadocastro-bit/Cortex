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
- An AI debt register documenting future risks around inference, provenance,
  semantic similarity, temporal parsing, scoring, evaluation, and reporting.
- Tests proving memory, source-trust, timeline, graph, and claim-matrix behavior.

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
      correlation_guard.py
      graph.py
      independence.py
      models.py
      memory.py
      text.py
      timeline.py
  tests/
    test_memory_merge.py
    test_phase2_evidence_trust.py
    test_phase3_investigative_graph.py
    test_phase4_associative_retrieval.py
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
