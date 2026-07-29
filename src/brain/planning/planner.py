import uuid

from brain.planning.action import Action
from brain.planning.blocker import Blocker, BlockerSeverity
from brain.planning.context import PlanningContext
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal
from brain.planning.plan import Plan, PlanStatus
from brain.planning.strategies.strategy import PlanningStrategy


class PlanningEngine:
    def __init__(self, strategy: PlanningStrategy) -> None:
        self._strategy = strategy

    def create_plan(
        self,
        goal: Goal,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...] = (),
        context: PlanningContext | None = None,
    ) -> Plan:
        ordered = self._strategy.organize(actions, dependencies)

        blockers = tuple(
            Blocker(
                action_id=a.id,
                description=f"Action {a.title} is pending review",
                severity=BlockerSeverity.LOW,
            )
            for a in ordered
            if a.dependencies
        )

        confidence = self._calculate_confidence(ordered, dependencies, blockers)

        return Plan(
            goal=goal,
            actions=ordered,
            dependencies=dependencies,
            blockers=blockers,
            confidence=confidence,
            status=PlanStatus.DRAFT,
        )

    def _calculate_confidence(
        self,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...],
        blockers: tuple[Blocker, ...],
    ) -> float:
        if not actions:
            return 1.0

        base = 1.0

        dep_penalty = len(dependencies) * 0.02
        base -= dep_penalty

        blocker_penalty = len(blockers) * 0.05
        base -= blocker_penalty

        return max(0.1, min(1.0, base))
