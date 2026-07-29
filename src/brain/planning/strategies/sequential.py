from brain.planning.action import Action
from brain.planning.dependency import Dependency
from brain.planning.strategies.strategy import PlanningStrategy


class SequentialStrategy(PlanningStrategy):
    def organize(
        self,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...],
    ) -> tuple[Action, ...]:
        return actions
