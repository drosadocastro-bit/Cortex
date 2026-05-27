"""In-memory relationship graph for structured investigation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import RelationshipEdge, RelationshipType


@dataclass(slots=True)
class FocusedGraphNeighborhood:
    """A bounded graph slice around a query node."""

    query_node_id: str
    nodes: dict[str, Any] = field(default_factory=dict)
    edges: list[RelationshipEdge] = field(default_factory=list)


@dataclass(slots=True)
class RelationshipGraphEngine:
    """Maintain nodes and provenance-carrying edges without duplicate buildup."""

    nodes: dict[str, Any] = field(default_factory=dict)
    edges: dict[tuple[str, str, RelationshipType, str], RelationshipEdge] = field(
        default_factory=dict
    )

    def add_node(self, node: Any) -> Any:
        self.nodes[node.id] = node
        return node

    def add_edge(self, edge: RelationshipEdge) -> RelationshipEdge:
        key = (edge.from_node_id, edge.to_node_id, edge.relation, edge.source_id)
        existing = self.edges.get(key)
        if existing is None:
            edge.confidence = _clamp(edge.confidence)
            self.edges[key] = edge
            return edge

        existing.confidence = max(existing.confidence, _clamp(edge.confidence))
        existing.evidence_ids.update(edge.evidence_ids)
        if edge.notes and edge.notes not in existing.notes:
            existing.notes = "; ".join(note for note in [existing.notes, edge.notes] if note)
        return existing

    def neighbors(
        self,
        node_id: str,
        *,
        relation: RelationshipType | None = None,
    ) -> list[Any]:
        neighbor_ids = {
            edge.to_node_id
            for edge in self.edges.values()
            if edge.from_node_id == node_id and (relation is None or edge.relation is relation)
        }
        neighbor_ids.update(
            edge.from_node_id
            for edge in self.edges.values()
            if edge.to_node_id == node_id and (relation is None or edge.relation is relation)
        )
        return [self.nodes[neighbor_id] for neighbor_id in neighbor_ids if neighbor_id in self.nodes]

    def contradiction_edges(self, node_id: str) -> list[RelationshipEdge]:
        return [
            edge
            for edge in self.edges.values()
            if edge.relation is RelationshipType.CONTRADICTS
            and (edge.from_node_id == node_id or edge.to_node_id == node_id)
        ]

    def source_lineage_chain(self, source_node_id: str) -> list[str]:
        chain = [source_node_id]
        seen = {source_node_id}
        current = source_node_id
        while True:
            next_edge = next(
                (
                    edge
                    for edge in self.edges.values()
                    if edge.from_node_id == current
                    and edge.relation is RelationshipType.DERIVED_FROM
                    and edge.to_node_id not in seen
                ),
                None,
            )
            if next_edge is None:
                return chain
            current = next_edge.to_node_id
            seen.add(current)
            chain.append(current)

    def neighborhood(self, query_node_id: str, *, depth: int = 1) -> FocusedGraphNeighborhood:
        result = FocusedGraphNeighborhood(query_node_id=query_node_id)
        if query_node_id not in self.nodes:
            return result

        visited = {query_node_id}
        queue: deque[tuple[str, int]] = deque([(query_node_id, 0)])
        result.nodes[query_node_id] = self.nodes[query_node_id]

        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            connected = [
                edge
                for edge in self.edges.values()
                if edge.from_node_id == current or edge.to_node_id == current
            ]
            for edge in connected:
                if edge not in result.edges:
                    result.edges.append(edge)
                other = edge.to_node_id if edge.from_node_id == current else edge.from_node_id
                if other in self.nodes:
                    result.nodes[other] = self.nodes[other]
                if other not in visited:
                    visited.add(other)
                    queue.append((other, current_depth + 1))
        return result
