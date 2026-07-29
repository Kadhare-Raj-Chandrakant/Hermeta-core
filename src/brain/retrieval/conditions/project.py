from brain.domain.task import Task
from brain.retrieval.condition import TriggerCondition


class ProjectCondition(TriggerCondition):
    def __init__(self, projects: tuple[str, ...]) -> None:
        self._projects = projects

    def matches(self, task: Task) -> bool:
        return task.project in self._projects

    @property
    def projects(self) -> tuple[str, ...]:
        return self._projects
