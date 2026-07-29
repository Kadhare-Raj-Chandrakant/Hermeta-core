from brain.domain.enums import KnowledgeType
from brain.domain.task import Task
from brain.retrieval.condition import TriggerCondition


class KnowledgeTypeCondition(TriggerCondition):
    def __init__(self, knowledge_types: tuple[KnowledgeType, ...]) -> None:
        self._knowledge_types = knowledge_types

    def matches(self, task: Task) -> bool:
        return True

    @property
    def knowledge_types(self) -> tuple[KnowledgeType, ...]:
        return self._knowledge_types
