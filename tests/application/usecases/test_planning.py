import uuid
from unittest.mock import MagicMock

import pytest

from brain.application.usecases.models import PlanDTO, PlanningRequest, PlanningSummary
from brain.application.usecases.planning import PlanningUseCase
from brain.domain.task import Priority, TaskType
from brain.planning.action import Action
from brain.planning.context import PlanningContext
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal
from brain.planning.plan import Plan
from brain.planning.planner import PlanningEngine
from brain.planning.strategies.sequential import SequentialStrategy


def _make_engine() -> PlanningEngine:
    return PlanningEngine(strategy=SequentialStrategy())


def _make_goal() -> Goal:
    return Goal(
        title="Test Goal",
        description="A test goal",
        project="test-project",
        priority=Priority.MEDIUM,
    )


def _make_actions(goal_id: uuid.UUID | None = None) -> tuple[Action, ...]:
    gid = goal_id or uuid.uuid4()
    return (
        Action(goal_id=gid, title="Action 1", description="First action"),
        Action(goal_id=gid, title="Action 2", description="Second action"),
    )


def _make_request() -> PlanningRequest:
    return PlanningRequest(
        task_type=TaskType.IMPLEMENT,
        project="hermes-brain",
        component="workflow",
        objective="Implement workflow orchestration",
    )


class TestConstruction:
    def test_stores_engine(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        assert use_case.engine is engine

    def test_creates_with_real_engine(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        assert isinstance(use_case.engine, PlanningEngine)


class TestDelegation:
    def test_execute_delegates_to_engine(self):
        engine = MagicMock(spec=PlanningEngine)
        expected = MagicMock(spec=Plan)
        engine.create_plan.return_value = expected

        use_case = PlanningUseCase(engine=engine)
        goal = _make_goal()
        actions = _make_actions(goal.id)
        deps = (Dependency(from_action_id=uuid.uuid4(), to_action_id=uuid.uuid4(), reason="test dependency"),)
        ctx = MagicMock(spec=PlanningContext)

        result = use_case.execute(goal, actions, deps, ctx)

        engine.create_plan.assert_called_once_with(goal, actions, deps, ctx)
        assert result is expected

    def test_execute_returns_engine_result(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        goal = _make_goal()
        actions = _make_actions(goal.id)

        result = use_case.execute(goal, actions)

        assert isinstance(result, Plan)
        assert result.goal is goal

    def test_arguments_forwarded_unchanged(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.return_value = MagicMock(spec=Plan)

        use_case = PlanningUseCase(engine=engine)
        goal = _make_goal()
        actions = _make_actions(goal.id)

        use_case.execute(goal, actions)

        call_args = engine.create_plan.call_args
        assert call_args[0][0] is goal
        assert call_args[0][1] is actions


class TestExecuteRequest:
    def test_execute_request_returns_planning_summary(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        result = use_case.execute_request(request)
        assert isinstance(result, PlanningSummary)

    def test_execute_request_stores_plan(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        summary = use_case.execute_request(request)
        plan = use_case.get_plan(summary.plan_id)
        assert isinstance(plan, PlanDTO)

    def test_execute_request_creates_goal(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.return_value = Plan(
            goal=Goal(title="test", description="test", project="test", priority=Priority.MEDIUM),
            actions=(),
            dependencies=(),
            blockers=(),
            confidence=0.8,
        )
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        use_case.execute_request(request)

        call_args = engine.create_plan.call_args[0]
        goal = call_args[0]
        assert isinstance(goal, Goal)
        assert goal.title == "Implement workflow orchestration"
        assert goal.project == "hermes-brain"
        assert goal.description == "implement: workflow"

    def test_execute_request_creates_action(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.return_value = Plan(
            goal=Goal(title="test", description="test", project="test", priority=Priority.MEDIUM),
            actions=(),
            dependencies=(),
            blockers=(),
            confidence=0.8,
        )
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        use_case.execute_request(request)

        call_args = engine.create_plan.call_args[0]
        actions = call_args[1]
        assert len(actions) == 1
        assert isinstance(actions[0], Action)
        assert actions[0].title == "Implement workflow orchestration"

    def test_execute_request_action_references_goal(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.return_value = Plan(
            goal=Goal(title="test", description="test", project="test", priority=Priority.MEDIUM),
            actions=(),
            dependencies=(),
            blockers=(),
            confidence=0.8,
        )
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        use_case.execute_request(request)

        call_args = engine.create_plan.call_args[0]
        goal = call_args[0]
        actions = call_args[1]
        assert actions[0].goal_id == goal.id

    def test_execute_request_called_exactly_once(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.return_value = Plan(
            goal=Goal(title="test", description="test", project="test", priority=Priority.MEDIUM),
            actions=(),
            dependencies=(),
            blockers=(),
            confidence=0.8,
        )
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        use_case.execute_request(request)
        assert engine.create_plan.call_count == 1

    def test_execute_request_with_real_engine(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        result = use_case.execute_request(request)

        assert isinstance(result, PlanningSummary)
        assert result.goal_count == 1
        assert result.action_count == 1

    def test_execute_request_plan_id_valid(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        summary = use_case.execute_request(request)
        assert isinstance(summary.plan_id, uuid.UUID)

    def test_execute_request_plan_status_draft(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        summary = use_case.execute_request(request)
        assert summary.plan_status == "draft"


class TestGetPlan:
    def test_get_plan_returns_stored_plan(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()
        summary = use_case.execute_request(request)
        plan = use_case.get_plan(summary.plan_id)
        assert isinstance(plan, PlanDTO)
        assert plan.plan_id == summary.plan_id

    def test_get_plan_raises_for_unknown_id(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        with pytest.raises(KeyError):
            use_case.get_plan(uuid.uuid4())


class TestStatelessness:
    def test_two_calls_produce_independent_results(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        goal = _make_goal()
        actions = _make_actions(goal.id)

        r1 = use_case.execute(goal, actions)
        r2 = use_case.execute(goal, actions)

        assert r1 is not r2
        assert r1.goal is r2.goal

    def test_two_requests_produce_independent_summaries(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        request = _make_request()

        s1 = use_case.execute_request(request)
        s2 = use_case.execute_request(request)

        assert s1.plan_id != s2.plan_id


class TestImmutability:
    def test_frozen(self):
        engine = _make_engine()
        use_case = PlanningUseCase(engine=engine)
        with pytest.raises(AttributeError):
            use_case.engine = None


class TestNoHiddenLogic:
    def test_no_transformation(self):
        engine = MagicMock(spec=PlanningEngine)
        sentinel = MagicMock(spec=Plan)
        engine.create_plan.return_value = sentinel

        use_case = PlanningUseCase(engine=engine)
        result = use_case.execute(_make_goal(), _make_actions())

        assert result is sentinel

    def test_no_exception_swallowing(self):
        engine = MagicMock(spec=PlanningEngine)
        engine.create_plan.side_effect = RuntimeError("boom")

        use_case = PlanningUseCase(engine=engine)
        with pytest.raises(RuntimeError, match="boom"):
            use_case.execute(_make_goal(), _make_actions())
