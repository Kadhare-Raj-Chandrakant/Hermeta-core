import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.models import ExecutionRequest, ExecutionSummary
from brain.application.usecases.planning import PlanningUseCase
from brain.execution.context import ExecutionContext
from brain.execution.executor import ExecutionEngine
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.policy import ExecutionPolicy
from brain.execution.report import ExecutionReport
from brain.execution.result import ExecutionResult
from brain.planning.plan import Plan


def _make_engine() -> ExecutionEngine:
    return ExecutionEngine(registry=HandlerRegistry(), policy=ExecutionPolicy())


def _make_plan() -> Plan:
    return Plan(
        goal=MagicMock(),
        actions=(),
        dependencies=(),
        blockers=(),
        confidence=1.0,
        status="draft",
    )


def _make_planning() -> PlanningUseCase:
    planning = MagicMock(spec=PlanningUseCase)
    planning.get_plan.return_value = _make_plan()
    return planning


def _make_request() -> ExecutionRequest:
    return ExecutionRequest(plan_id=uuid.uuid4(), project="hermes-brain")


def _make_report() -> ExecutionReport:
    return ExecutionReport(
        plan_id=uuid.uuid4(),
        results=(
            ExecutionResult(record=MagicMock(), success=True, output="ok"),
        ),
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )


class TestConstruction:
    def test_stores_engine(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        assert use_case.engine is engine

    def test_stores_planning(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        assert use_case.planning is planning

    def test_creates_with_real_engine(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        assert isinstance(use_case.engine, ExecutionEngine)


class TestDelegation:
    def test_execute_delegates_to_engine(self):
        engine = MagicMock(spec=ExecutionEngine)
        expected = _make_report()
        engine.execute.return_value = expected

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        request = _make_request()

        result = use_case.execute(request)

        engine.execute.assert_called_once()
        call_args = engine.execute.call_args[0]
        assert isinstance(call_args[0], Plan)
        assert isinstance(call_args[1], ExecutionContext)
        assert call_args[1].plan_id == request.plan_id

    def test_execute_returns_execution_summary(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        request = _make_request()

        result = use_case.execute(request)

        assert isinstance(result, ExecutionSummary)

    def test_execute_retrieves_plan_from_planning(self):
        engine = MagicMock(spec=ExecutionEngine)
        engine.execute.return_value = _make_report()

        planning = MagicMock(spec=PlanningUseCase)
        plan = _make_plan()
        planning.get_plan.return_value = plan

        use_case = ExecutionUseCase(engine=engine, planning=planning)
        request = _make_request()
        use_case.execute(request)

        planning.get_plan.assert_called_once_with(request.plan_id)

    def test_execute_constructs_execution_context(self):
        engine = MagicMock(spec=ExecutionEngine)
        engine.execute.return_value = _make_report()

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)

        metadata = (("key", "value"),)
        request = ExecutionRequest(
            plan_id=uuid.uuid4(), project="test-project", metadata=metadata,
        )
        use_case.execute(request)

        call_args = engine.execute.call_args[0]
        ctx = call_args[1]
        assert ctx.plan_id == request.plan_id
        assert ctx.project == "test-project"
        assert ctx.metadata == metadata


class TestSummarize:
    def test_summary_success_when_no_failures(self):
        engine = MagicMock(spec=ExecutionEngine)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(
                ExecutionResult(record=MagicMock(), success=True, output="ok"),
                ExecutionResult(record=MagicMock(), success=True, output="ok"),
            ),
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            completed_at=datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc),
        )
        engine.execute.return_value = report

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.execution_success is True
        assert result.executed_action_count == 2
        assert result.failed_action_count == 0
        assert result.cancelled_action_count == 0

    def test_summary_failure_when_failures(self):
        engine = MagicMock(spec=ExecutionEngine)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(
                ExecutionResult(record=MagicMock(), success=True, output="ok"),
                ExecutionResult(record=MagicMock(), success=False, output="", error="boom"),
            ),
            started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            completed_at=datetime(2026, 1, 1, 0, 0, 3, tzinfo=timezone.utc),
        )
        engine.execute.return_value = report

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.execution_success is False
        assert result.executed_action_count == 2
        assert result.failed_action_count == 1

    def test_summary_duration(self):
        engine = MagicMock(spec=ExecutionEngine)
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=start,
            completed_at=end,
        )
        engine.execute.return_value = report

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.execution_duration == timedelta(seconds=10)

    def test_summary_started_and_completed(self):
        engine = MagicMock(spec=ExecutionEngine)
        engine.execute.return_value = _make_report()

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.execution_started is True
        assert result.execution_completed is True

    def test_summary_with_empty_results(self):
        engine = MagicMock(spec=ExecutionEngine)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        engine.execute.return_value = report

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.executed_action_count == 0
        assert result.failed_action_count == 0
        assert result.execution_success is True

    def test_summary_all_results_accounted(self):
        engine = MagicMock(spec=ExecutionEngine)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(
                ExecutionResult(record=MagicMock(), success=True, output="ok"),
                ExecutionResult(record=MagicMock(), success=False, output="", error="fail"),
                ExecutionResult(record=MagicMock(), success=False, output="", error="fail"),
            ),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        engine.execute.return_value = report

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        result = use_case.execute(_make_request())

        assert result.executed_action_count == 3
        assert result.failed_action_count == 2
        assert result.cancelled_action_count == 0


class TestStatelessness:
    def test_two_calls_produce_independent_results(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)

        r1 = use_case.execute(_make_request())
        r2 = use_case.execute(_make_request())

        assert r1 is not r2


class TestImmutability:
    def test_frozen(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        with pytest.raises(AttributeError):
            use_case.engine = None

    def test_cannot_reassign_planning(self):
        engine = _make_engine()
        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        with pytest.raises(AttributeError):
            use_case.planning = None


class TestNoHiddenLogic:
    def test_no_exception_swallowing(self):
        engine = MagicMock(spec=ExecutionEngine)
        engine.execute.side_effect = RuntimeError("boom")

        planning = _make_planning()
        use_case = ExecutionUseCase(engine=engine, planning=planning)
        with pytest.raises(RuntimeError, match="boom"):
            use_case.execute(_make_request())

    def test_planning_failure_propagates(self):
        engine = MagicMock(spec=ExecutionEngine)
        planning = MagicMock(spec=PlanningUseCase)
        planning.get_plan.side_effect = KeyError("missing plan")

        use_case = ExecutionUseCase(engine=engine, planning=planning)
        with pytest.raises(KeyError):
            use_case.execute(_make_request())
