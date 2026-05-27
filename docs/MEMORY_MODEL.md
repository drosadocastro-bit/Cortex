# Memory Model

The memory model treats investigation as uncertainty-preserving cognition. A
memory is not a truth claim. It is a weighted record with provenance, activation
history, contradiction pressure, and possible archival state.

## Sensory Memory

Sensory memory is the first landing zone for raw observations, notes, document
fragments, or reports. In the framework this is represented by `EvidenceItem`.
It records source, time, summary, tags, and confidence without asserting that
the observed content is true.

## Attention Filtering

Attention filtering determines which evidence-backed memories become active.
Phase 1 models this through `MemoryActivationEngine`. Activation increments
`activation_count`, updates `last_activated_at`, and increases
`memory_strength` within a hard `0.0` to `1.0` bound.

## Episodic Memory

`MemoryRecord` represents an episodic investigative memory: a bounded remembered
idea connected to evidence ids, tags, activation state, contradiction pressure,
and related memories.

Important fields include:

- `memory_strength`: current cognitive weight.
- `activation_count`: repeated attention or use.
- `last_activated_at`: time anchor for decay.
- `contradiction_pressure`: unresolved conflict load.
- `archival`: low-prominence state for weak memories.
- `linked_memory_ids`: associative and contradiction links.
- `source_confidence`: optional source-confidence signal.

The legacy `strength` field remains aligned with `memory_strength` for backward
compatibility.

## Semantic Compression

`SemanticCompressionEngine` creates deterministic summaries from duplicate,
near-duplicate, or topic-equivalent memories. It does not use an LLM, vector
database, or probabilistic summarizer.

Compressed memories preserve:

- merged memory ids
- strongest tags
- total activation count
- average contradiction pressure
- highest source confidence when present

Compression reduces clutter without treating repetition as proof.

## Associative Activation

Activation strengthens memories that are repeatedly useful. This supports
working investigation patterns where relevant memories become easier to surface.
Activation is bounded so repetition cannot create certainty.

An archival memory may return to active status only when reactivation pushes its
strength across a clear threshold.

## Memory Decay

`MemoryDecayEngine` applies time-aware decay based on days since the last
activation. Unused memories gradually lose strength. Weak unused memories decay
faster, while contradiction pressure slows decay so unresolved conflicts are not
silently erased.

Memory strength is always clamped between `0.0` and `1.0`.

## Archival Transition

When a memory falls below the archival threshold, it is marked `archival=True`.
Archival records remain available for provenance, later review, and possible
reactivation. They are not deleted.

## Contradiction Preservation

`ContradictionPressureEngine` links conflicting memories and increases
`contradiction_pressure` on both records. It also marks records as needing review
and preserving uncertainty.

Contradictions are not automatically resolved. Neither memory overwrites the
other, and neither is deleted merely because conflict exists.

## Retrieval Priority

Vector similarity may later help locate candidates, but it remains secondary.
Investigation should prefer:

1. Source provenance and trust.
2. Timeline placement.
3. Graph relationships.
4. Explicit contradiction state.
5. Vector similarity as an assistive index.
