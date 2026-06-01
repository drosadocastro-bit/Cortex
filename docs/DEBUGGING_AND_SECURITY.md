# Debugging And Security Hygiene

This project is a deterministic research framework. Security hygiene here means
checking that the current local code does not accidentally cross its stated
boundaries.

## Local Checks

Recommended maintenance checks:

```powershell
python -m pytest
rg "import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml.load|os.system" src tests
python -m pytest tests/test_phase13_2_hygiene.py
```

The first command verifies behavior. The second looks for network, process,
dynamic execution, or unsafe deserialization patterns. The third looks for
encoding artifacts in documentation through the hygiene test without embedding
the artifact markers in this file.

## Phase 14-18 Claim Pipeline Check

After claim extraction, normalization, evaluation, and review docket work, run:

```powershell
python -m pytest tests/test_phase18_2_consolidation.py
```

This verifies that the claim pipeline remains ordered, non-mutating, and
documented. It also checks the Phase 14-18 modules for the same risky network,
process, dynamic execution, and unsafe deserialization patterns.

## Phase 19-23 Review And Demo Check

After source review, working memory, session persistence, bundle export, and
demo workspace work, run:

```powershell
python -m pytest tests/test_phase23_2_consolidation.py
```

This verifies that demo data remains synthetic, review bundles preserve
limitations, session loads do not apply decisions to graph state, and bundle
guardrails do not confuse `provenance` with certainty language.

## Dependency Surface

Project dependencies are defined in `pyproject.toml`, not by the global Python
environment. The current runtime environment may contain many unrelated
packages, but the project dependency surface is intentionally small:

- `networkx`
- `python-dateutil`
- `pytest` as a development dependency

Future dependency additions should explain why standard library behavior is
insufficient and should sit behind deterministic wrappers when possible.

## Persistence Safety

Snapshot loading reads JSON and reconstructs project records. It must never:

- execute loaded data
- import code from a snapshot
- create claims, evidence, graph edges, or truth state automatically
- discard unknown fields silently

`PersistenceStore`, `Serializer`, `SnapshotValidator`, and
`PersistenceGuardrails` should remain the safety boundary for local snapshots.

Session persistence follows the same local JSON discipline. `SessionPersistenceStore`
must never execute loaded data or apply review decisions to evidence, claims,
source trust, graph records, or truth state automatically.

## CLI Safety

The CLI harness uses synthetic deterministic fixtures. It should not call the
network, invoke external commands, or treat prompts as executable instructions.

## Known Non-Issues

The global environment may include packages such as web clients, LLM libraries,
or vector libraries installed for other work. That does not make them project
dependencies unless they appear in `pyproject.toml` or are imported by `src`.

## Future Hardening

Before adding live LLM inference, web UI, connectors, VLM perception, or vector
databases, add checks for:

- prompt-like instruction contamination
- metadata visibility boundaries
- resource budgets for duplicate floods
- provenance-preserving importers
- no automatic artifact promotion across the reality boundary
