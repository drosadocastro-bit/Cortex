"""NetworkX graph backend with deterministic traversal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from roswell_uap_cortex.graph_backend import GraphBackend, GraphTraversalResult
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import RelationshipEdge, RelationshipType


@dataclass(slots=True)
class NetworkXGraphBackend(GraphBackend):
    """NetworkX MultiDiGraph backend that preserves provenance and edge types."""

    graph: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)
    edges_by_key: dict[tuple[str, str, RelationshipType, str], RelationshipEdge] = field(
        default_factory=dict
    )

    def add_node(self, node_id: str, **metadata: Any) -> None:
        existing = dict(self.graph.nodes[node_id]) if self.graph.has_node(node_id) else {}
        existing.update(metadata)
        self.graph.add_node(node_id, **existing)

    def add_edge(self, edge: RelationshipEdge) -> RelationshipEdge:
        key = self._edge_key(edge)
        existing = self.edges_by_key.get(key)
        if existing is None:
            edge.confidence = _clamp(edge.confidence)
            self.edges_by_key[key] = edge
            self.graph.add_edge(
                edge.from_node_id,
                edge.to_node_id,
                key=self._key_string(key),
                relation=edge.relation.value,
                source_id=edge.source_id,
                confidence=edge.confidence,
                evidence_ids=sorted(edge.evidence_ids),
                notes=edge.notes,
                edge_id=edge.id,
            )
            return edge

        existing.confidence = max(existing.confidence, _clamp(edge.confidence))
        existing.evidence_ids.update(edge.evidence_ids)
        if edge.notes and edge.notes not in existing.notes:
            existing.notes = "; ".join(note for note in [existing.notes, edge.notes] if note)
        self.graph[existing.from_node_id][existing.to_node_id][self._key_string(key)].update(
            confidence=existing.confidence,
            evidence_ids=sorted(existing.evidence_ids),
            notes=existing.notes,
        )
        return existing

    def get_neighbors(
        self,
        node_id: str,
        relation: RelationshipType | None = None,
    ) -> list[str]:
        neighbors: set[str] = set()
        for edge in self._edges_touching(node_id, relation):
            other = edge.to_node_id if edge.from_node_id == node_id else edge.from_node_id
            neighbors.add(other)
        return sorted(neighbors)

    def get_contradictions(self, node_id: str) -> list[RelationshipEdge]:
        return self._sorted_edges(self._edges_touching(node_id, RelationshipType.CONTRADICTS))

    def get_lineage_paths(self, source_node_id: str) -> list[list[str]]:
        paths: list[list[str]] = []

        def walk(current: str, path: list[str]) -> None:
            next_nodes = [
                edge.to_node_id
                for edge in self._sorted_edges(self.edges_by_key.values())
                if edge.from_node_id == current
                and edge.relation is RelationshipType.DERIVED_FROM
                and edge.to_node_id not in path
            ]
            if not next_nodes:
                paths.append(path)
                return
            for next_node in sorted(next_nodes):
                walk(next_node, [*path, next_node])

        walk(source_node_id, [source_node_id])
        return sorted(paths, key=lambda path: (len(path), path))

    def subgraph(self, node_id: str, *, depth: int = 1) -> GraphTraversalResult:
        if not self.graph.has_node(node_id):
            return GraphTraversalResult()
        visited = {node_id}
        frontier = [(node_id, 0)]
        edges: list[RelationshipEdge] = []
        while frontier:
            current, current_depth = frontier.pop(0)
            if current_depth >= depth:
                continue
            for edge in self._sorted_edges(self._edges_touching(current)):
                if edge not in edges:
                    edges.append(edge)
                other = edge.to_node_id if edge.from_node_id == current else edge.from_node_id
                if other not in visited:
                    visited.add(other)
                    frontier.append((other, current_depth + 1))
            frontier.sort(key=lambda item: item[0])
        return GraphTraversalResult(node_ids=sorted(visited), edges=self._sorted_edges(edges))

    def timeline_linked_traversal(self, node_id: str) -> list[str]:
        temporal = {
            RelationshipType.TEMPORAL_BEFORE,
            RelationshipType.TEMPORAL_AFTER,
            RelationshipType.SAME_EVENT_CANDIDATE,
        }
        neighbors = {
            edge.to_node_id if edge.from_node_id == node_id else edge.from_node_id
            for edge in self.edges_by_key.values()
            if (edge.from_node_id == node_id or edge.to_node_id == node_id)
            and edge.relation in temporal
        }
        return sorted(neighbors)

    def _edges_touching(
        self,
        node_id: str,
        relation: RelationshipType | None = None,
    ) -> list[RelationshipEdge]:
        return [
            edge
            for edge in self.edges_by_key.values()
            if (edge.from_node_id == node_id or edge.to_node_id == node_id)
            and (relation is None or edge.relation is relation)
        ]

    def _sorted_edges(self, edges) -> list[RelationshipEdge]:
        return sorted(
            edges,
            key=lambda edge: (
                edge.from_node_id,
                edge.to_node_id,
                edge.relation.value,
                edge.source_id,
                edge.id,
            ),
        )

    def _edge_key(self, edge: RelationshipEdge) -> tuple[str, str, RelationshipType, str]:
        return (edge.from_node_id, edge.to_node_id, edge.relation, edge.source_id)

    def _key_string(self, key: tuple[str, str, RelationshipType, str]) -> str:
        return "|".join([key[0], key[1], key[2].value, key[3]])
