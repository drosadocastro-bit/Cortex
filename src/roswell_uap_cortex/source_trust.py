"""Source trust scoring for uncertain evidence domains."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import SourceTrust


MEDIA_RISK = {
    "official_record": 0.05,
    "archival_document": 0.1,
    "transcript": 0.2,
    "news": 0.3,
    "book": 0.35,
    "forum": 0.55,
    "youtube": 0.65,
    "tiktok": 0.75,
    "fiction": 0.9,
    "unknown": 0.6,
}


@dataclass(slots=True)
class SourceTrustEngine:
    """Compute trust and risk without deciding truth."""

    contamination_penalty: float = 0.08

    def evaluate(self, source: SourceTrust) -> SourceTrust:
        media_risk = MEDIA_RISK.get(source.media_type, MEDIA_RISK["unknown"])
        trust = (
            source.reliability * 0.18
            + source.transparency * 0.12
            + source.corroboration_history * 0.1
            + source.source_authority * 0.16
            + source.chain_of_custody * 0.18
            + (1 - source.publication_distance) * 0.12
            + (1 - source.redaction_level) * 0.08
            + source.independent_corroboration * 0.06
        )
        risk = (
            (1 - source.reliability) * 0.14
            + (1 - source.transparency) * 0.1
            + (1 - source.chain_of_custody) * 0.18
            + source.publication_distance * 0.12
            + source.redaction_level * 0.12
            + media_risk * 0.18
            + len(source.contamination_flags) * self.contamination_penalty
            + (1 - source.independent_corroboration) * 0.08
        )

        source.source_trust_score = _clamp(trust)
        source.source_risk_score = _clamp(risk)
        return source
