"""Coverage summaries for synthetic evaluation scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import EvaluationScenario, ExpectedBehaviorType
from roswell_uap_cortex.scenarios import ScenarioFactory


@dataclass(slots=True)
class SyntheticScenarioDataset:
    """Inspect synthetic scenario coverage without claiming real-world validity."""

    scenarios: list[EvaluationScenario] = field(default_factory=list)
    tag_counts: dict[str, int] = field(default_factory=dict)
    behavior_counts: dict[str, int] = field(default_factory=dict)
    risk_level_counts: dict[str, int] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    @property
    def scenario_count(self) -> int:
        return len(self.scenarios)


@dataclass(slots=True)
class ScenarioDatasetBuilder:
    """Build deterministic summaries for the synthetic evaluation dataset."""

    factory: ScenarioFactory = field(default_factory=ScenarioFactory)

    def build(self, scenarios: list[EvaluationScenario] | None = None) -> SyntheticScenarioDataset:
        scenarios = scenarios or self.factory.all()
        return SyntheticScenarioDataset(
            scenarios=sorted(scenarios, key=lambda item: item.scenario_id),
            tag_counts=self._tag_counts(scenarios),
            behavior_counts=self._behavior_counts(scenarios),
            risk_level_counts=self._risk_level_counts(scenarios),
            limitations=[
                "synthetic scenarios evaluate framework behavior only",
                "scenario coverage is not real-world validation",
                "passing scenarios do not certify operational use",
            ],
        )

    def _tag_counts(self, scenarios: list[EvaluationScenario]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for scenario in scenarios:
            for tag in scenario.tags:
                counts[tag] = counts.get(tag, 0) + 1
        return dict(sorted(counts.items()))

    def _behavior_counts(self, scenarios: list[EvaluationScenario]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for scenario in scenarios:
            for expected in scenario.expected_behaviors:
                behavior = expected.behavior
                key = behavior.value if isinstance(behavior, ExpectedBehaviorType) else str(behavior)
                counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items()))

    def _risk_level_counts(self, scenarios: list[EvaluationScenario]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for scenario in scenarios:
            counts[scenario.risk_level] = counts.get(scenario.risk_level, 0) + 1
        return dict(sorted(counts.items()))
