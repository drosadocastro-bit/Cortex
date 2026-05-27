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
- Tests proving duplicate memories merge.

## Project Layout

```text
Roswell-uap-cortex/
  docs/
    MEMORY_MODEL.md
    PROBLEM_STATEMENT.md
  src/
    roswell_uap_cortex/
      __init__.py
      models.py
      memory.py
  tests/
    test_memory_merge.py
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
