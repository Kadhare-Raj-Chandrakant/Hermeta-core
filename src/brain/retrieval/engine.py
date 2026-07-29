import uuid

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task
from brain.retrieval.conditions.knowledge_type import KnowledgeTypeCondition
from brain.retrieval.request import RetrievalRequest
from brain.retrieval.trigger import RetrievalTrigger


class RetrievalTriggerEngine:
    def __init__(self, triggers: tuple[RetrievalTrigger, ...]) -> None:
        self._triggers = triggers

    def evaluate(self, task: Task) -> tuple[RetrievalRequest, ...]:
        matching: list[RetrievalTrigger] = []
        for trigger in self._triggers:
            if not trigger.enabled:
                continue
            if trigger.condition.matches(task):
                matching.append(trigger)

        matching.sort(key=lambda t: t.priority, reverse=True)

        if not matching:
            return ()

        trigger_ids: list[uuid.UUID] = []
        all_knowledge_types: set[KnowledgeType] = set()
        reasons: list[str] = []

        for trigger in matching:
            trigger_ids.append(trigger.id)
            condition = trigger.condition
            if isinstance(condition, KnowledgeTypeCondition):
                all_knowledge_types.update(condition.knowledge_types)
            reasons.append(trigger.description)

        return (
            RetrievalRequest(
                task=task,
                trigger_ids=tuple(trigger_ids),
                knowledge_types=tuple(all_knowledge_types),
                reason="; ".join(reasons),
            ),
        )
