import uuid
from dataclasses import dataclass, field

from brain.application.usecases.models import PlanDTO, PlanningRequest, PlanningSummary
from brain.domain.enums import KnowledgeType
from brain.domain.task import Priority
from brain.planning.action import Action
from brain.planning.context import PlanningContext
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal
from brain.planning.plan import Plan
from brain.planning.planner import PlanningEngine


@dataclass(frozen=True)
class PlanningUseCase:
    engine: PlanningEngine
    _plans: dict[uuid.UUID, Plan] = field(default_factory=dict, repr=False)

    def _execute(
        self,
        goal: Goal,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...] = (),
        context: PlanningContext | None = None,
    ) -> Plan:
        """Internal method for direct engine access - use execute_request for DTO boundary."""
        return self.engine.create_plan(goal, actions, dependencies, context)

    # Public alias for internal engine access (tests and workflow)
    execute = _execute

    def execute_request(self, request: PlanningRequest) -> PlanningSummary:
        goal = Goal(
            title=request.objective,
            description=f"{request.task_type.value}: {request.component}",
            project=request.project,
            priority=Priority.MEDIUM,
        )
        actions = (
            Action(
                goal_id=goal.id,
                title=goal.title,
                description=goal.description,
                required_knowledge=(KnowledgeType.TASK,),
            ),
        )
        plan = self.engine.create_plan(goal, actions)
        self._plans[plan.id] = plan
        return PlanningSummary(
            plan_id=plan.id,
            plan_status=plan.status.value,
            goal_count=1,
            action_count=len(plan.actions),
            dependency_count=len(plan.dependencies),
            blocker_count=len(plan.blockers),
        )

    def get_plan(self, plan_id: uuid.UUID) -> PlanDTO:
        plan = self._plans[plan_id]
        return PlanDTO(
            plan_id=plan.id,
            plan_status=plan.status.value,
            goal_title=plan.goal.title,
            goal_description=plan.goal.description,
            project=plan.goal.project,
            action_count=len(plan.actions),
            dependency_count=len(plan.dependencies),
            blocker_count=len(plan.blockers),
        )