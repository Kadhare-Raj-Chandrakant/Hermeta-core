import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.domain.task import Priority
from brain.planning.action import Action, ActionStatus
from brain.planning.blocker import Blocker, BlockerSeverity
from brain.planning.context import PlanningContext
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal, GoalStatus
from brain.planning.plan import Plan, PlanStatus
from brain.planning.planner import PlanningEngine
from brain.planning.strategies.sequential import SequentialStrategy
from brain.planning.strategies.dependency import DependencyStrategy


def make_goal(**kwargs) -> Goal:
    defaults = dict(
        title="Test Goal",
        description="Test description",
        project="test_project",
        priority=Priority.HIGH,
    )
    defaults.update(kwargs)
    return Goal(**defaults)


def make_action(title: str = "Action", goal_id: uuid.UUID | None = None, **kwargs) -> Action:
    defaults = dict(
        goal_id=goal_id or uuid.uuid4(),
        title=title,
        description=f"Description for {title}",
    )
    defaults.update(kwargs)
    return Action(**defaults)


class TestPlanningEngineCreation:
    def test_create_with_sequential(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        assert engine is not None

    def test_create_with_dependency(self):
        engine = PlanningEngine(strategy=DependencyStrategy())
        assert engine is not None


class TestPlanningEngineBehavior:
    def test_creates_plan(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        actions = (make_action("A"), make_action("B"))
        plan = engine.create_plan(goal, actions)
        assert isinstance(plan, Plan)
        assert plan.goal is goal
        assert len(plan.actions) == 2

    def test_injected_strategy_used(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        a1 = make_action("First")
        a2 = make_action("Second")
        plan = engine.create_plan(goal, (a1, a2))
        assert plan.actions[0].title == "First"
        assert plan.actions[1].title == "Second"

    def test_context_accepted(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        ctx = PlanningContext(
            task_id=uuid.uuid4(),
            knowledge_types=(KnowledgeType.ARCHITECTURE,),
            constraints=("must use Python",),
        )
        plan = engine.create_plan(goal, (), context=ctx)
        assert isinstance(plan, Plan)

    def test_immutable_result(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        plan = engine.create_plan(goal, ())
        with pytest.raises(AttributeError):
            plan.actions = ()

    def test_empty_actions(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        plan = engine.create_plan(goal, ())
        assert plan.actions == ()
        assert plan.confidence == 1.0

    def test_plan_status_is_draft(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        plan = engine.create_plan(goal, ())
        assert plan.status == PlanStatus.DRAFT

    def test_blockers_created_for_actions_with_dependencies(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        a1 = make_action("A")
        a2 = make_action("B", dependencies=(a1.id,))
        plan = engine.create_plan(goal, (a1, a2))
        assert len(plan.blockers) == 1
        assert plan.blockers[0].action_id == a2.id
        assert plan.blockers[0].severity == BlockerSeverity.LOW

    def test_no_blockers_for_independent_actions(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        a1 = make_action("A")
        a2 = make_action("B")
        plan = engine.create_plan(goal, (a1, a2))
        assert len(plan.blockers) == 0

    def test_confidence_decreases_with_dependencies(self):
        engine = PlanningEngine(strategy=SequentialStrategy())
        goal = make_goal()
        a1 = make_action("A")
        a2 = make_action("B", dependencies=(a1.id,))
        plan = engine.create_plan(goal, (a1, a2))
        assert plan.confidence < 1.0
