from brain.domain.task import Task
from brain.retrieval.condition import TriggerCondition


class ComponentCondition(TriggerCondition):
    def __init__(self, components: tuple[str, ...]) -> None:
        self._components = components

    def matches(self, task: Task) -> bool:
        return task.component in self._components

    @property
    def components(self) -> tuple[str, ...]:
        return self._components
