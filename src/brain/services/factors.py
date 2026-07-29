from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.version import KnowledgeVersion
from brain.services.scoring import ScoringFactor


class IntentMatch(ScoringFactor):
    def __init__(self, weight: float = 0.4) -> None:
        self._weight = weight

    @property
    def name(self) -> str:
        return "intent_match"

    @property
    def weight(self) -> float:
        return self._weight

    def score(self, intent: str, version: KnowledgeVersion) -> float:
        intent_lower = intent.lower()
        title_lower = version.title.lower()
        understanding_lower = version.understanding.lower()
        title_words = set(title_lower.split())
        intent_words = set(intent_lower.split())

        if intent_lower == title_lower:
            return 1.0
        if intent_words == title_words:
            return 0.9
        if len(intent_words) > 1 and intent_words <= title_words:
            return 0.8
        if intent_words & title_words:
            return 0.5
        if intent_lower in understanding_lower:
            return 0.7
        return 0.0


class KnowledgePriority(ScoringFactor):
    _type_scores: dict[KnowledgeType, float] = {
        KnowledgeType.DECISION: 1.0,
        KnowledgeType.ARCHITECTURE: 0.9,
        KnowledgeType.RULE: 0.85,
        KnowledgeType.BUG: 0.8,
        KnowledgeType.PATTERN: 0.75,
        KnowledgeType.COMPONENT: 0.7,
        KnowledgeType.TASK: 0.6,
        KnowledgeType.GOAL: 0.55,
        KnowledgeType.ASSUMPTION: 0.5,
        KnowledgeType.QUESTION: 0.4,
        KnowledgeType.DISCOVERY: 0.3,
    }

    def __init__(self, weight: float = 0.2) -> None:
        self._weight = weight

    @property
    def name(self) -> str:
        return "knowledge_priority"

    @property
    def weight(self) -> float:
        return self._weight

    def score(self, intent: str, version: KnowledgeVersion) -> float:
        return self._type_scores.get(version.knowledge_type, 0.5)


class RelationshipDistance(ScoringFactor):
    def __init__(self, weight: float = 0.15) -> None:
        self._weight = weight

    @property
    def name(self) -> str:
        return "relationship_distance"

    @property
    def weight(self) -> float:
        return self._weight

    def score(self, intent: str, version: KnowledgeVersion) -> float:
        if not version.relationships:
            return 0.5
        return min(1.0, 0.5 + len(version.relationships) * 0.1)


class LifecycleStateFactor(ScoringFactor):
    _state_scores: dict[LifecycleState, float] = {
        LifecycleState.ACTIVE: 1.0,
        LifecycleState.DRAFT: 0.6,
        LifecycleState.ARCHIVED: 0.2,
    }

    def __init__(self, weight: float = 0.15) -> None:
        self._weight = weight

    @property
    def name(self) -> str:
        return "lifecycle_state"

    @property
    def weight(self) -> float:
        return self._weight

    def score(self, intent: str, version: KnowledgeVersion) -> float:
        return self._state_scores.get(version.lifecycle_state, 0.5)


class RecencyFactor(ScoringFactor):
    def __init__(self, weight: float = 0.1) -> None:
        self._weight = weight

    @property
    def name(self) -> str:
        return "recency"

    @property
    def weight(self) -> float:
        return self._weight

    def score(self, intent: str, version: KnowledgeVersion) -> float:
        return min(1.0, version.version_number / 10.0)


DEFAULT_FACTORS: list[ScoringFactor] = [
    IntentMatch(weight=0.4),
    KnowledgePriority(weight=0.2),
    RelationshipDistance(weight=0.15),
    LifecycleStateFactor(weight=0.15),
    RecencyFactor(weight=0.1),
]
