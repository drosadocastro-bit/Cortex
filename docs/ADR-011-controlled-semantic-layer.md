# ADR-011: Controlled Semantic Layer

## Status

Accepted.

## Context

Semantic search is useful for retrieval, but it is dangerous if introduced
before provenance, lineage, contradiction preservation, reasoning guardrails,
discourse, persistence, and evaluation are established.

Phase 10 introduces a vector-ready semantic layer without real embedding models
or vector databases.

## Decision

Add controlled semantic infrastructure:

- `EmbeddingBackend` defines the future embedding interface.
- `MockEmbeddingBackend` provides deterministic token-hash embeddings.
- `SemanticSimilarityEngine` compares records using mock embeddings, lexical
  overlap, tags, entities, source independence, lineage overlap, and
  contradiction pressure.
- `SemanticClusterEngine` creates `possible_related_cluster` groups.
- `HybridRetrievalCoordinator` combines associative, graph, timeline, and
  semantic retrieval signals while preserving component scores.
- `SemanticContaminationGuard` propagates semantic warnings.

## Rationale

### Embeddings Are Secondary

Semantic similarity can help retrieve context, but it cannot confirm claims or
establish truth. Provenance, lineage, contradiction, and source independence
remain primary.

### Similarity Is Not Confirmation

Semantic matches may reflect paraphrase, copying, or same-lineage echoes.
Similarity results carry warnings and never create graph support edges.

### Clustering Is Not Equivalence

Clusters are labeled `possible_related_cluster`. They preserve member ids,
duplicate lineage, and contested members without claiming that records are the
same event, same claim, or independently corroborating.

### Lineage And Provenance Constrain Scores

Same-lineage matches are downgraded. Missing provenance produces warnings.
Fictional contamination and contested status propagate into semantic outputs.

### Mock Embeddings First

Mock embeddings keep the default behavior deterministic while preserving a
future backend path for local sentence-transformers, OpenAI embeddings, Ollama
embeddings, LM Studio-compatible embedding endpoints, and vector databases.

## Consequences

The project is vector-ready without depending on a vector database or real
embedding service. Future vector integration must honor the same abstraction and
guardrails.
