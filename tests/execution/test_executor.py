import uuid
from datetime import datetime, timedelta, timezone

import pytest

from brain.execution.context import ExecutionContext
from brain.execution.errors import NoHandlerError
from brain.execution.executor import ExecutionEngine
from brain.execution.handlers.handler import ActionHandler
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.observer import ExecutionObserver
from brain.execution.policy import ExecutionPolicy
from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.planning.action import Action
from brain.planning.goal import Goal, GoalStatus
from brain.planning.plan import Plan, PlanStatus
from brain.domain.task import Priority


def make_action(title: str = "Action", **kwargs) -> Action:
    defaults = dict(goal_id=uuid.uuid4(), title=title, description=f"Desc for {title}")
    defaults.update(kwargs)
    return Action(**defaults)


def make_goal(**kwargs) -> Goal:
    defaults = dict(title="Test Goal", description="Test", project="test", priority=Priority.HIGH)
    defaults.update(kwargs)
    return Goal(**defaults)


def make_plan(actions: tuple[Action, ...] = (), **kwargs) -> Plan:
    defaults = dict(goal=make_goal(), actions=actions, dependencies=(), blockers=(), confidence=0.8)
    defaults.update(kwargs)
    return Plan(**defaults)


class SuccessHandler(ActionHandler):
    def can_handle(self, action: Action) -> bool:
        return True

    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        record = ExecutionRecord(
            action_id=action.id,
            status=ExecutionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
        )
        return ExecutionResult(record=record, success=True, output=f"Done: {action.title}")


class FailHandler(ActionHandler):
    def can_handle(self, action: Action) -> bool:
        return action.title == "Fail"

    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        record = ExecutionRecord(
            action_id=action.id,
            status=ExecutionStatus.FAILED,
            started_at=datetime.now(timezone.utc),
        )
        return ExecutionResult(record=record, success=False, output="", error="Intentional failure")


class SelectiveHandler(ActionHandler):
    def can_handle(self, action: Action) -> bool:
        return action.title == "Specific"

    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        record = ExecutionRecord(
            action_id=action.id,
            status=ExecutionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
        )
        return ExecutionResult(record=record, success=True, output="Specific done")


class TestExecutionEngineCreation:
    def test_create(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        assert engine is not None


class TestExecutionEngineEmptyPlan:
    def test_empty_plan(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        plan = make_plan(actions=())
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.total_actions == 0
        assert report.plan_id == plan.id


class TestExecutionEngineSingleAction:
    def test_single_action(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a = make_action("Do something")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.total_actions == 1
        assert report.completed == 1
        assert report.results[0].output == "Done: Do something"


class TestExecutionEngineMultipleActions:
    def test_multiple_actions(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a1 = make_action("First")
        a2 = make_action("Second")
        a3 = make_action("Third")
        plan = make_plan(actions=(a1, a2, a3))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.total_actions == 3
        assert report.completed == 3

    def test_preserves_order(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a1 = make_action("Alpha")
        a2 = make_action("Beta")
        plan = make_plan(actions=(a1, a2))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.results[0].output == "Done: Alpha"
        assert report.results[1].output == "Done: Beta"


class TestExecutionEngineMissingHandler:
    def test_missing_handler_raises(self):
        reg = HandlerRegistry()
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a = make_action("No handler")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        with pytest.raises(NoHandlerError):
            engine.execute(plan, ctx)


class TestExecutionEngineFailure:
    def test_failed_handler(self):
        reg = HandlerRegistry()
        reg.register(FailHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a = make_action("Fail")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.failed == 1
        assert report.completed == 0

    def test_stop_on_failure(self):
        reg = HandlerRegistry()
        reg.register(FailHandler())
        engine = ExecutionEngine(
            registry=reg,
            policy=ExecutionPolicy(stop_on_failure=True),
        )
        a1 = make_action("Fail")
        a2 = make_action("Never reached")
        plan = make_plan(actions=(a1, a2))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.total_actions == 1

    def test_continue_after_failure(self):
        reg = HandlerRegistry()
        reg.register(FailHandler())
        reg.register(SuccessHandler())
        engine = ExecutionEngine(
            registry=reg,
            policy=ExecutionPolicy(stop_on_failure=False),
        )
        a1 = make_action("Fail")
        a2 = make_action("Success")
        plan = make_plan(actions=(a1, a2))
        ctx = ExecutionContext(plan_id=plan.id)
        report = engine.execute(plan, ctx)
        assert report.total_actions == 2
        assert report.failed == 1
        assert report.completed == 1


class TestExecutionEngineObserver:
    def test_observer_notifications(self):
        class TrackingObserver(ExecutionObserver):
            def __init__(self):
                self.started = []
                self.completed = []
                self.failed = []

            def on_started(self, record):
                self.started.append(record)

            def on_completed(self, result):
                self.completed.append(result)

            def on_failed(self, result):
                self.failed.append(result)

        observer = TrackingObserver()
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(
            registry=reg,
            policy=ExecutionPolicy(),
            observers=(observer,),
        )
        a = make_action("Observed")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        engine.execute(plan, ctx)
        assert len(observer.started) == 1
        assert len(observer.completed) == 1
        assert len(observer.failed) == 0

    def test_observer_on_failure(self):
        class TrackingObserver(ExecutionObserver):
            def __init__(self):
                self.failed = []

            def on_failed(self, result):
                self.failed.append(result)

        observer = TrackingObserver()
        reg = HandlerRegistry()
        reg.register(FailHandler())
        engine = ExecutionEngine(
            registry=reg,
            policy=ExecutionPolicy(),
            observers=(observer,),
        )
        a = make_action("Fail")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        engine.execute(plan, ctx)
        assert len(observer.failed) == 1


class TestExecutionEngineDeterministic:
    def test_deterministic_output(self):
        reg = HandlerRegistry()
        reg.register(SuccessHandler())
        engine = ExecutionEngine(registry=reg, policy=ExecutionPolicy())
        a = make_action("Test")
        plan = make_plan(actions=(a,))
        ctx = ExecutionContext(plan_id=plan.id)
        r1 = engine.execute(plan, ctx)
        r2 = engine.execute(plan, ctx)
        assert r1.total_actions == r2.total_actions
        assert r1.completed == r2.completed
