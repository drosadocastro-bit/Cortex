"""Deterministic attention and salience scoring."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.attention_guardrails import AttentionGuardrails
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    AttentionCandidate,
    AttentionDecision,
    AttentionFocus,
    AttentionPolicy,
    AttentionSignal,
    AttentionWarning,
    AttentionWarningType,
    SalienceScore,
)
from roswell_uap_cortex.salience_policy import SaliencePolicyEngine
from roswell_uap_cortex.text import SimpleTokenizer, overlap_score


@dataclass(slots=True)
class AttentionEngine:
    """Score review salience without producing confidence or confirmation."""

    policy_engine: SaliencePolicyEngine = field(default_factory=SaliencePolicyEngine)
    guardrails: AttentionGuardrails = field(default_factory=AttentionGuardrails)
    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)

    def score(
        self,
        candidate: AttentionCandidate,
        focus: AttentionFocus | None = None,
        policy: AttentionPolicy | str | None = None,
        *,
        lineage_seen: set[str] | None = None,
    ) -> SalienceScore:
        focus = focus or AttentionFocus()
        policy = self._policy(policy or focus.investigation_mode)
        lineage_seen = lineage_seen or set()

        focus_match = self._focus_match(candidate, focus)
        provenance_fragility = 1.0 if not candidate.provenance_ids else _clamp(candidate.metadata.get("provenance_fragility", 0.0))
        recurrence = _clamp(candidate.recurrence)
        if candidate.lineage_id and candidate.lineage_id in lineage_seen:
            recurrence = min(recurrence, 0.25)

        components = {
            AttentionSignal.RELEVANCE: _clamp(max(focus_match, candidate.metadata.get("relevance", 0.0))),
            AttentionSignal.NOVELTY: _clamp(candidate.novelty),
            AttentionSignal.CONTRADICTION_PRESSURE: _clamp(candidate.contradiction_pressure),
            AttentionSignal.PROVENANCE_FRAGILITY: provenance_fragility,
            AttentionSignal.SOURCE_TRUST: _clamp(candidate.source_trust),
            AttentionSignal.SOURCE_INDEPENDENCE: _clamp(candidate.source_independence),
            AttentionSignal.TEMPORAL_IMPORTANCE: _clamp(candidate.temporal_importance),
            AttentionSignal.CONTAMINATION_RISK: _clamp(candidate.contamination_risk),
            AttentionSignal.RECURRENCE: recurrence,
            AttentionSignal.UNCERTAINTY_LOAD: _clamp(candidate.uncertainty_load),
            AttentionSignal.USER_FOCUS_MATCH: focus_match,
        }
        final = sum(components[signal] * policy.weights.get(signal, 0.0) for signal in components)
        if candidate.archived and candidate.novelty < 0.6 and candidate.contradiction_pressure == 0:
            final *= 0.6
        if candidate.lineage_id and candidate.lineage_id in lineage_seen:
            final *= 0.72
        if candidate.contested or candidate.contradiction_pressure > 0:
            final = max(final, 0.58)
        if not candidate.provenance_ids:
            final = max(final, 0.25)
        if candidate.contamination_risk > 0:
            final = max(final, 0.45)

        warnings = self.guardrails.warnings_for(candidate)
        if candidate.lineage_id and candidate.lineage_id in lineage_seen:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.SAME_LINEAGE_DOWNGRADED,
                    "Repeated same-lineage records are downgraded so they do not dominate attention.",
                    {candidate.record_id},
                )
            )

        return SalienceScore(
            component_scores=components,
            final_salience_score=_clamp(final),
            reason_codes=self._reason_codes(candidate, components, lineage_seen),
            warnings=warnings,
        )

    def prioritize(
        self,
        candidates: list[AttentionCandidate],
        focus: AttentionFocus | None = None,
        policy: AttentionPolicy | str | None = None,
        *,
        limit: int = 8,
    ) -> AttentionDecision:
        focus = focus or AttentionFocus()
        policy = self._policy(policy or focus.investigation_mode)
        lineage_seen: set[str] = set()
        scored: list[tuple[AttentionCandidate, SalienceScore]] = []
        for candidate in sorted(candidates, key=lambda item: item.record_id):
            score = self.score(candidate, focus, policy, lineage_seen=lineage_seen)
            scored.append((candidate, score))
            if candidate.lineage_id:
                lineage_seen.add(candidate.lineage_id)

        ranked = sorted(
            scored,
            key=lambda item: (
                item[0].contested or item[0].contradiction_pressure > 0,
                item[1].final_salience_score,
                item[0].record_id,
            ),
            reverse=True,
        )
        selected_pairs = ranked[:limit]
        selected = [candidate for candidate, _ in selected_pairs]
        deferred = [candidate for candidate, _ in ranked[limit:]]
        review = [
            candidate
            for candidate, score in ranked
            if candidate.contested
            or candidate.contradiction_pressure > 0
            or candidate.contamination_risk > 0
            or not candidate.provenance_ids
            or score.final_salience_score >= 0.5
        ][:limit]
        context = [
            candidate
            for candidate, score in ranked
            if candidate.provenance_ids
            and candidate.contamination_risk < 0.8
            and not candidate.speculative
            and score.final_salience_score >= 0.25
        ][:limit]

        salience_by_id = {candidate.record_id: score for candidate, score in scored}
        warnings = [
            warning
            for _, score in scored
            for warning in score.warnings
            if warning.warning_type is not AttentionWarningType.SALIENCE_NOT_BELIEF
        ]
        warnings.append(
            AttentionWarning(
                AttentionWarningType.SALIENCE_NOT_BELIEF,
                "Attention selection is review priority, not belief or truth confidence.",
                {candidate.record_id for candidate in selected},
            )
        )

        return AttentionDecision(
            selected_records=selected,
            selected_for_context=context,
            selected_for_review=review,
            deferred_records=deferred,
            archived_records_considered=[candidate for candidate in candidates if candidate.archived],
            salience_by_id=salience_by_id,
            attention_warnings=sorted(warnings, key=lambda item: (item.warning_type.value, sorted(item.related_ids))),
        )

    def _focus_match(self, candidate: AttentionCandidate, focus: AttentionFocus) -> float:
        term_score = overlap_score(self.tokenizer.tokenize(" ".join([candidate.label, candidate.text])), focus.focus_terms)
        entity_score = 1.0 if candidate.entity_ids.intersection(focus.target_entities) else 0.0
        event_score = 1.0 if candidate.event_ids.intersection(focus.target_event_ids) else 0.0
        topic_score = 1.0 if candidate.claim_topics.intersection(focus.target_claim_topics) else 0.0
        return _clamp(max(term_score, entity_score, event_score, topic_score))

    def _policy(self, policy: AttentionPolicy | str) -> AttentionPolicy:
        if isinstance(policy, AttentionPolicy):
            return policy
        return self.policy_engine.policy(policy)

    def _reason_codes(
        self,
        candidate: AttentionCandidate,
        components: dict[AttentionSignal, float],
        lineage_seen: set[str],
    ) -> list[str]:
        reasons: list[str] = []
        for signal, value in sorted(components.items(), key=lambda item: item[0].value):
            if value >= 0.5:
                reasons.append(signal.value)
        if not candidate.provenance_ids:
            reasons.append("missing_provenance_review")
        if candidate.lineage_id and candidate.lineage_id in lineage_seen:
            reasons.append("same_lineage_downgraded")
        if candidate.archived:
            reasons.append("archived_record_considered")
        if candidate.contested:
            reasons.append("contested_record_preserved")
        return reasons
