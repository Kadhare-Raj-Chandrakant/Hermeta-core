from dataclasses import dataclass

from brain.domain.version import KnowledgeVersion
from brain.services.factors import DEFAULT_FACTORS
from brain.services.scoring import ScoringFactor


@dataclass(frozen=True)
class ScoredVersion:
    version: KnowledgeVersion
    score: float
    breakdown: dict[str, float]


class RelevanceEngine:
    def __init__(self, factors: list[ScoringFactor] | None = None) -> None:
        self._factors = factors if factors is not None else list(DEFAULT_FACTORS)

    def rank(self, intent: str, versions: list[KnowledgeVersion]) -> list[ScoredVersion]:
        if not versions:
            return []

        scored = [self._score_version(intent, v) for v in versions]
        return sorted(scored, key=lambda s: (s.score, s.version.version_number), reverse=True)

    def _score_version(self, intent: str, version: KnowledgeVersion) -> ScoredVersion:
        total_weight = sum(f.weight for f in self._factors)
        weighted_sum = 0.0
        breakdown: dict[str, float] = {}

        for factor in self._factors:
            raw = factor.score(intent, version)
            weighted_sum += raw * factor.weight
            breakdown[factor.name] = raw

        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        return ScoredVersion(version=version, score=final_score, breakdown=breakdown)
