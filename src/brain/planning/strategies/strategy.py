from abc import ABC, abstractmethod

from brain.planning.action import Action
from brain.planning.dependency import Dependency


class PlanningStrategy(ABC):
    @abstractmethod
    def organize(
        self,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...],
    ) -> tuple[Action, ...]:
        ...
