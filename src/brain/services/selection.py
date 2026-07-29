from dataclasses import dataclass

from brain.domain.enums import KnowledgeType
from brain.domain.version import KnowledgeVersion
from brain.domain.task import Task, TaskType
from brain.services.relevance import ScoredVersion


@dataclass(frozen=True)
class SelectionPolicy:
    required: tuple[KnowledgeType, ...]
    preferred: tuple[KnowledgeType, ...]
    optional: tuple[KnowledgeType, ...]
    supplemental: tuple[KnowledgeType, ...]


@dataclass(frozen=True)
class SelectedKnowledgePackage:
    selected: tuple[KnowledgeVersion, ...]
    budget_used: int
    budget_remaining: int


DEFAULT_POLICIES: dict[TaskType, SelectionPolicy] = {
    TaskType.IMPLEMENT: SelectionPolicy(
        required=(KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT),
        preferred=(KnowledgeType.DECISION, KnowledgeType.PATTERN),
        optional=(KnowledgeType.RULE, KnowledgeType.GOAL),
        supplemental=(KnowledgeType.ASSUMPTION, KnowledgeType.DISCOVERY),
    ),
    TaskType.DEBUG: SelectionPolicy(
        required=(KnowledgeType.BUG, KnowledgeType.COMPONENT),
        preferred=(KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION),
        optional=(KnowledgeType.PATTERN, KnowledgeType.RULE),
        supplemental=(KnowledgeType.QUESTION, KnowledgeType.DISCOVERY),
    ),
    TaskType.REVIEW: SelectionPolicy(
        required=(KnowledgeType.ARCHITECTURE, KnowledgeType.RULE),
        preferred=(KnowledgeType.DECISION, KnowledgeType.PATTERN),
        optional=(KnowledgeType.COMPONENT, KnowledgeType.GOAL),
        supplemental=(KnowledgeType.ASSUMPTION, KnowledgeType.QUESTION),
    ),
    TaskType.REFACTOR: SelectionPolicy(
        required=(KnowledgeType.ARCHITECTURE, KnowledgeType.PATTERN),
        preferred=(KnowledgeType.DECISION, KnowledgeType.COMPONENT),
        optional=(KnowledgeType.RULE, KnowledgeType.GOAL),
        supplemental=(KnowledgeType.ASSUMPTION, KnowledgeType.DISCOVERY),
    ),
    TaskType.TEST: SelectionPolicy(
        required=(KnowledgeType.COMPONENT, KnowledgeType.RULE),
        preferred=(KnowledgeType.PATTERN, KnowledgeType.DECISION),
        optional=(KnowledgeType.ARCHITECTURE, KnowledgeType.BUG),
        supplemental=(KnowledgeType.QUESTION, KnowledgeType.DISCOVERY),
    ),
    TaskType.DOCUMENT: SelectionPolicy(
        required=(KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT),
        preferred=(KnowledgeType.GOAL, KnowledgeType.DECISION),
        optional=(KnowledgeType.PATTERN, KnowledgeType.RULE),
        supplemental=(KnowledgeType.QUESTION, KnowledgeType.DISCOVERY),
    ),
    TaskType.OPTIMIZE: SelectionPolicy(
        required=(KnowledgeType.COMPONENT, KnowledgeType.PATTERN),
        preferred=(KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION),
        optional=(KnowledgeType.RULE, KnowledgeType.GOAL),
        supplemental=(KnowledgeType.DISCOVERY, KnowledgeType.QUESTION),
    ),
    TaskType.INTEGRATE: SelectionPolicy(
        required=(KnowledgeType.COMPONENT, KnowledgeType.ARCHITECTURE),
        preferred=(KnowledgeType.DECISION, KnowledgeType.PATTERN),
        optional=(KnowledgeType.RULE, KnowledgeType.GOAL),
        supplemental=(KnowledgeType.ASSUMPTION, KnowledgeType.QUESTION),
    ),
}


class SelectionEngine:
    def __init__(
        self,
        policies: dict[TaskType, SelectionPolicy] | None = None,
        max_versions: int = 10,
    ) -> None:
        self._policies = policies if policies is not None else dict(DEFAULT_POLICIES)
        self._max_versions = max_versions

    def select(
        self, task: Task, ranked: list[ScoredVersion]
    ) -> SelectedKnowledgePackage:
        policy = self._policies.get(task.task_type)
        if policy is None:
            return SelectedKnowledgePackage(selected=(), budget_used=0, budget_remaining=len(ranked))

        required_available = {
            v.version.knowledge_type
            for v in ranked
            if v.version.knowledge_type in policy.required
        }
        if not set(policy.required) <= required_available:
            return SelectedKnowledgePackage(selected=(), budget_used=0, budget_remaining=len(ranked))

        selected: list[KnowledgeVersion] = []
        remaining_budget = self._max_versions

        for category in [policy.required, policy.preferred, policy.optional, policy.supplemental]:
            for version_score in ranked:
                if remaining_budget <= 0:
                    break
                if version_score.version.knowledge_type in category:
                    if version_score.version not in selected:
                        selected.append(version_score.version)
                        remaining_budget -= 1

        selected_sorted = sorted(selected, key=lambda v: (v.knowledge_type.value, v.title))

        return SelectedKnowledgePackage(
            selected=tuple(selected_sorted),
            budget_used=len(selected_sorted),
            budget_remaining=self._max_versions - len(selected_sorted),
        )
