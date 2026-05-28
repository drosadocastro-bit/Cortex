"""Graph backend abstraction for deterministic graph infrastructure."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from roswell_uap_cortex.models import RelationshipEdge, RelationshipType


@dataclass(slots=True)
class GraphTraversalResult:
    """Deterministic graph traversal result."""

    node_ids: list[str] = field(default_factory=list)
    edges: list[RelationshipEdge] = field(default_factory=list)


class GraphBackend(ABC):
    """Abstract graph operations used by advanced graph infrastructure."""

    @abstractmethod
    def add_node(self, node_id: str, **metadata: Any) -> None:
        """Add or update a graph node."""

    @abstractmethod
    def add_edge(self, edge: RelationshipEdge) -> RelationshipEdge:
        """Add or merge an edge without duplicate accumulation."""

    @abstractmethod
    def get_neighbors(
        self,
        node_id: str,
        relation: RelationshipType | None = None,
    ) -> list[str]:
        """Return deterministic neighboring node ids."""

    @abstractmethod
    def get_contradictions(self, node_id: str) -> list[RelationshipEdge]:
        """Return contradiction edges touching a node."""

    @abstractmethod
    def get_lineage_paths(self, source_node_id: str) -> list[list[str]]:
        """Return deterministic derived-from lineage paths."""

    @abstractmethod
    def subgraph(self, node_id: str, *, depth: int = 1) -> GraphTraversalResult:
        """Extract a deterministic focused subgraph."""

    @abstractmethod
    def timeline_linked_traversal(self, node_id: str) -> list[str]:
        """Traverse temporal neighbors deterministically."""
