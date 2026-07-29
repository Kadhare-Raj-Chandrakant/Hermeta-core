from brain.domain.task import Task, TaskType
from brain.retrieval.condition import TriggerCondition


class TaskTypeCondition(TriggerCondition):
    def __init__(self, task_types: tuple[TaskType, ...]) -> None:
        self._task_types = task_types

    def matches(self, task: Task) -> bool:
        return task.task_type in self._task_types

    @property
    def task_types(self) -> tuple[TaskType, ...]:
        return self._task_types
