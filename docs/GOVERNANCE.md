# Governance

Roswell UAP Cortex should grow through deliberate research phases, not feature
accumulation. Governance here means preserving the framework's conceptual
discipline as much as its tests.

## Recurring Consolidation Rule

Every five major phases, pause feature expansion for an architecture
consolidation, debugging, and security hygiene pass.

These pauses are part of the framework design, not cleanup afterthoughts. Their
purpose is to preserve:

- conceptual clarity
- public API discipline
- documentation accuracy
- adversarial honesty
- dependency and security hygiene
- epistemic boundaries
- the canonical end-to-end flow

## Cadence

The current cadence is:

- Phase 13.2: architecture consolidation, debugging, and security hygiene
- Phase 18.2: next planned consolidation
- Phase 23.2: future consolidation
- Phase 28.2: future consolidation

The exact number can shift if the framework accumulates risk earlier, but five
major phases is the default checkpoint.

## Consolidation Checklist

Each consolidation pass should check:

- Does the architecture map still match the implementation?
- Does the public API surface remain intentional?
- Have new modules created overlapping concepts?
- Are uncertainty, provenance, lineage, contradiction, and reality boundaries
  still visible?
- Do docs explain why new subsystems exist?
- Do adversarial findings and remediation debt remain current?
- Are dependency and security surfaces still minimal?
- Do tests pass?

## Rule Of Thumb

If a phase adds power, a later consolidation phase should add clarity.
