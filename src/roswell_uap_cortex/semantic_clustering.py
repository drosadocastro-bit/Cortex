"""Controlled semantic clustering."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from roswell_uap_cortex.models import SemanticCluster, SemanticRecord, SemanticWarning
from roswell_uap_cortex.semantic import SemanticSimilarityEngine


@dataclass(slots=True)
class SemanticClusterEngine:
    """Group possibly related records without implying equivalence."""

    similarity_engine: SemanticSimilarityEngine = field(default_factory=SemanticSimilarityEngine)
    threshold: float = 0.35

    def cluster(self, records: list[SemanticRecord]) -> list[SemanticCluster]:
        clusters: list[SemanticCluster] = []
        assigned: set[str] = set()
        ordered = sorted(records, key=lambda record: record.record_id)
        for record in ordered:
            if record.record_id in assigned:
                continue
            members = {record.record_id}
            warnings: list[SemanticWarning] = []
            for other in ordered:
                if other.record_id == record.record_id or other.record_id in assigned:
                    continue
                result = self.similarity_engine.compare(record, other)
                if result.similarity_score >= self.threshold:
                    members.add(other.record_id)
                    warnings.extend(result.warning_flags)
            assigned.update(members)
            member_records = [item for item in ordered if item.record_id in members]
            lineage_counts: dict[str, int] = {}
            for item in member_records:
                if item.lineage_id:
                    lineage_counts[item.lineage_id] = lineage_counts.get(item.lineage_id, 0) + 1
            duplicate_lineages = {
                lineage_id for lineage_id, count in lineage_counts.items() if count > 1
            }
            contested = {item.record_id for item in member_records if item.contested}
            clusters.append(
                SemanticCluster(
                    cluster_id=self._cluster_id(members),
                    member_ids=members,
                    duplicate_lineage_ids=duplicate_lineages,
                    contested_member_ids=contested,
                    warnings=self._dedupe_warnings(warnings),
                )
            )
        return sorted(clusters, key=lambda cluster: cluster.cluster_id)

    def _cluster_id(self, members: set[str]) -> str:
        joined = "|".join(sorted(members))
        return "semantic-cluster:" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]

    def _dedupe_warnings(self, warnings: list[SemanticWarning]) -> list[SemanticWarning]:
        deduped: dict[tuple[str, tuple[str, ...]], SemanticWarning] = {}
        for warning in warnings:
            key = (warning.warning_type.value, tuple(sorted(warning.related_ids)))
            deduped.setdefault(key, warning)
        return [deduped[key] for key in sorted(deduped)]
