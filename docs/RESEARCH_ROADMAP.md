# Research Roadmap

This document describes the next planned experiments for the Roswell UAP Cortex
framework. It is a **research agenda**, not a product roadmap. Each experiment is
framed as a question about how the framework behaves when exposed to a specific
class of epistemic challenge. There are no delivery dates; experiments advance when
the framework is ready and the question remains meaningful.

The overall goal is to understand how brain-inspired mechanisms — memory,
associative activation, contradiction handling, temporal ordering, and bounded
reasoning — interact when applied to noisy, unstructured, and contested evidence.
No experiment here is intended to produce operational results or authoritative
answers.

---

## Experiment 1 — Observation vs Interpretation Separation

### Research question

Can the ingestion layer reliably distinguish a direct observation ("a light was
seen moving at high speed") from an interpretation layered on top of it ("the
light was therefore an aircraft")? When the two are entangled in the same
sentence, how does the framework propagate that ambiguity downstream into memory,
retrieval, and discourse?

### Why it matters

One of the most common failure modes in noisy unstructured domains is that
interpretation gets stored at the same epistemic level as observation. Once
collapsed, the difference is invisible to later reasoning steps. If the framework
cannot preserve the boundary, downstream confidence estimates will be misleading
regardless of how carefully the rest of the pipeline is designed.

### Example inputs / test setup

- A raw text block that mixes first-person sensory description with explanatory
  framing in the same sentence.
- A quoted report where the original observer's words are wrapped in a
  secondary reporter's gloss.
- A document where "observed" and "believed" appear in adjacent sentences
  referring to the same event.

### What to observe / success criteria

- `ExtractedObservation` records carry a flag or confidence note that distinguishes
  observation-dominant spans from interpretation-dominant ones.
- Downstream `EvidenceItem` records do not silently upgrade interpreted spans to
  the same trust level as direct observations.
- Discourse output preserves the separation: interpretation sections do not appear
  in the "Observed Evidence" section without an explicit qualification.
- Ingestion warnings are generated when the boundary cannot be reliably determined.

---

## Experiment 2 — Lineage and Repeated-Source Bias

### Research question

When multiple input documents share a common lineage — one original report
republished, paraphrased, or quoted across several sources — does the framework
correctly suppress the artificial confidence boost that would otherwise result
from treating each copy as independent evidence?

### Why it matters

Repeated-source bias is endemic in noisy unstructured corpora. A single witness
account retold across ten publications can look like ten independent data points
if lineage is not tracked. The framework's `SourceLineageRecord`,
`CorrelationGuard`, and independence scoring exist specifically to address this,
but the mechanisms need to be stressed under realistic repetition patterns to
verify they hold.

### Example inputs / test setup

- One synthetic primary source and three derivative documents with varying degrees
  of paraphrase and attribution clarity.
- A case where the original source is never directly ingested, only its derivatives.
- A case where two genuinely independent sources happen to describe the same event
  using similar language.

### What to observe / success criteria

- `SourceLineageRecord` correctly traces derivative documents back to a common
  ancestor when attribution markers are present.
- `IndependenceScore` is lower for derivative sources than for structurally
  independent ones.
- `CorrelationGuard` downgrades association candidates that share lineage rather
  than treating them as corroboration.
- When the original source is missing, the framework does not conflate "widely
  repeated" with "well-supported"; ingestion warnings or confidence penalties
  reflect the incomplete lineage.
- The "Provenance Notes" section of discourse output makes repeated lineage
  visible rather than hiding it.

---

## Experiment 3 — Associative Activation vs Naive Retrieval

### Research question

Does the framework's associative activation model retrieve meaningfully different
and epistemically more cautious results than a naive similarity-ranked retrieval
approach? Specifically: does it surface contested and weakly-supported material
that a conventional top-K retrieval would bury, while avoiding false-corroboration
from high-overlap but low-independence candidates?

### Why it matters

If associative activation collapses into a conventional similarity search, the
careful epistemic architecture above the retrieval layer is undermined at its
foundation. This experiment tests whether the combination of lexical overlap, tag
overlap, entity overlap, timeline proximity, source independence scoring, and
contradiction pressure produces a qualitatively different activation profile —
not just a re-ranked similarity list.

### Example inputs / test setup

- A small synthetic corpus with: one high-quality independent source, two
  low-independence derivative sources covering the same event, one contested
  claim with a direct contradiction, and two genuinely unrelated documents.
- A query designed to match the contested claim on surface similarity.

### What to observe / success criteria

- `AssociationCandidate` objects for derivative sources show lower scores than the
  primary source despite similar surface-level relevance.
- The contested claim appears in `contested_associations` rather than the main
  activation list.
- The two unrelated documents do not appear in the activated context at all, or
  appear only with explicit weak-association labels.
- Activated context retains the contradiction rather than resolving it silently.
- Comparing the associative activation scores against a simple lexical similarity
  ranking of the same corpus shows a measurable difference in which candidates
  are promoted.

---

## Experiment 4 — Contradiction-Preserving Discourse

### Research question

When two or more evidence items directly contradict each other on a factual point,
does the discourse layer preserve both sides of the contradiction in its output —
including when the contradiction involves high-confidence and low-confidence
sources — without collapsing toward the "stronger" source or simply omitting the
weaker one?

### Why it matters

Contradiction resolution is one of the most consequential epistemic choices in any
reasoning system. A system that silently favors higher-confidence sources will
systematically suppress minority accounts, which in noisy unstructured domains may
turn out to be the most informative ones. The framework's design intention is to
preserve contradictions rather than resolve them — this experiment verifies that
intention holds through the full pipeline to the discourse output.

### Example inputs / test setup

- An `EvidenceItem` from a high-trust source asserting X.
- An `EvidenceItem` from a low-trust source asserting not-X (or a mutually
  exclusive alternative to X).
- A query that directly engages the contested point.
- A variant where both sources have identical trust levels.

### What to observe / success criteria

- Both sides of the contradiction appear in the "Contradictions" section of
  discourse output with their respective provenance and trust levels cited.
- Neither side is promoted to the "Observed Evidence" section without explicit
  qualification.
- The "Uncertainty Summary" section reflects the unresolved contradiction.
- The discourse guardrails prevent any narrative synthesis that implies one side is
  more true than the other without explicit analyst review.
- When trust levels are identical, neither source is silently preferred.

---

## Experiment 5 — Memory Formation and Decay

### Research question

When the same observation is ingested multiple times — across different inputs,
at different times, with varying levels of detail — does the memory layer
correctly reinforce a single consolidated memory record rather than accumulating
redundant copies? And when a memory is not accessed or reinforced over time, does
decay proceed at the expected rate without corrupting the evidence records the
memory points to?

### Why it matters

Memory is the mechanism by which the framework builds a persistent cognitive state
across multiple ingestion events. If duplicate ingestion creates redundant memory
records rather than reinforcing a canonical one, the system's long-term state will
inflate. If decay is not correctly bounded, memories may fade to the point where
relevant evidence is no longer retrievable — or decay may fail to apply at all,
leaving stale high-confidence records that should have been weakened. The
`MemoryDecayEngine` and duplicate merging logic exist to address this, but they
need validation under realistic multi-ingestion patterns.

### Example inputs / test setup

- Three ingestion events for the same underlying observation: the first as a
  complete source document, the second as a brief paraphrase two simulated time
  steps later, and the third as a fragment with missing provenance.
- A memory record that is never accessed after formation and decays across several
  simulated time steps.
- A memory record under sustained contradiction pressure to verify that
  contradiction damping applies correctly.

### What to observe / success criteria

- After three ingestions of the same observation, exactly one `MemoryRecord`
  exists (or a small number reflecting legitimately distinct perspectives), not
  three separate copies.
- The consolidated record's strength is higher than any single ingestion would
  have produced, reflecting reinforcement.
- The decaying record's strength decreases monotonically across simulated steps
  without reaching zero unless explicitly archived.
- The underlying `EvidenceItem` records are not modified by decay — only the
  memory's strength and activation metadata change.
- Contradiction pressure visibly reduces memory strength below what reinforcement
  alone would predict.
- A fresh retrieval after significant decay returns the decayed memory with a
  lower score than a recently reinforced equivalent, and the score difference is
  reflected in the `AssociationCandidate` ranking.

---

## Notes on Experimental Method

These experiments are not unit tests in the conventional sense. They are
behavioral probes: each one is designed to reveal whether a stated design
intention holds when the system is exposed to the specific class of input it was
designed to handle. Success criteria are framed in terms of observable framework
behavior — what appears in discourse output, what scores are assigned, what
warnings are generated — rather than in terms of "correctness" relative to a
ground truth that may not exist for noisy unstructured domains.

Negative results are as informative as positive ones. If an experiment reveals
that the framework does not yet preserve a boundary it was intended to preserve,
that is useful knowledge about where the architecture needs to develop next.
