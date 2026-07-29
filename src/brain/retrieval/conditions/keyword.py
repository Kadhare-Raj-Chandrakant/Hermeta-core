from brain.domain.task import Task
from brain.retrieval.condition import TriggerCondition


class KeywordCondition(TriggerCondition):
    def __init__(self, keywords: tuple[str, ...]) -> None:
        self._keywords = keywords

    def matches(self, task: Task) -> bool:
        objective_lower = task.objective.lower()
        return any(kw.lower() in objective_lower for kw in self._keywords)

    @property
    def keywords(self) -> tuple[str, ...]:
        return self._keywords
