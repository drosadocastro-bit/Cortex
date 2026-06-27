# Phase 30: Documentation Navigation And Scope Reorganization

Phase 30 is a documentation-only consolidation pass. It reorganizes how the
current framework is described so future phases have clearer landmarks and do
not extend a flat capability ledger.

It does not add runtime behavior, new inference, new scoring, new evidence
interpretation, new UI, or new external integration.

## Why This Exists

Cortex has accumulated many bounded subsystems: ingestion, provenance, lineage,
claims, graph memory, retrieval, reasoning, discourse, persistence, evaluation,
adversarial testing, presentation contracts, evidence quality, and review
bundles. The components remain conceptually disciplined, but the README was
becoming harder to navigate because every capability appeared at the same level.

This phase keeps the architecture understandable by grouping capabilities around
the evidence-first review path.

## What Changed

- The README table of contents now links directly to grouped Current Scope
  subsections.
- The Current Scope section is organized into:
  - Core Evidence And Memory
  - Ingestion And Provenance
  - Claims, Quality, And Review
  - Reasoning, Retrieval, And Discourse
  - Persistence, Evaluation, And Safety
  - Navigation Notes
- Navigation notes now point readers toward the current-state snapshot, workflow
  map, API and model map, adversarial results guide, and AI debt register.
- The current-state snapshot now treats README reorganization as completed
  documentation hygiene rather than a pending feature candidate.
- The AI debt register now tracks the risk that future additions could turn the
  grouped scope back into a flat capability ledger.

## Boundary

Documentation organization is not validation. Grouping related capabilities does
not make them more mature, more authoritative, or more operationally ready.

The README should remain a map of bounded mechanisms, not a product brochure or
an assurance case.

## Future Watchpoint

When a future phase adds a capability, place it in the most precise existing
section first. Add a new section only if the addition represents a genuinely new
architectural category rather than a renamed version of an existing one.
