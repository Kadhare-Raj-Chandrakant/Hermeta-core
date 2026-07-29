from abc import ABC, abstractmethod

from brain.domain.task import Task


class TriggerCondition(ABC):
    @abstractmethod
    def matches(self, task: Task) -> bool:
        ...
