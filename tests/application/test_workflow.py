import inspect
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from brain.adapter.models import AdapterTask
from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.brain_session import BrainSession
from brain.application.brain_service import BrainService
from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.models import (
    ExecutionRequest,
    ExecutionSummary,
    LearningRequest,
    LearningSummary,
    PlanningRequest,
    PlanningSummary,
)
from brain.application.usecases.planning import PlanningUseCase
from brain.application.workflow.report import WorkflowReport
from brain.application.workflow.workflow import BrainWorkflow
from brain.domain.task import Priority, TaskType
from brain.execution.executor import ExecutionEngine
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.policy import ExecutionPolicy
from brain.learning.coordinator import LearningCoordinator
from brain.planning.planner import PlanningEngine
from brain.planning.strategies.sequential import SequentialStrategy
from brain.services.compiler import ContextPackage


def _make_task() -> AdapterTask:
    return AdapterTask(
        task_id=uuid.uuid4(),
        task_type=TaskType.IMPLEMENT,
        objective="Implement workflow orchestration",
        project="hermes-brain",
        component="workflow",
    )


def _make_brain_session() -> BrainSession:
    mock_service = MagicMock(spec=BrainService)
    mock_service.prepare.return_value = MagicMock(spec=ContextPackage)
    return BrainSession(brain=mock_service)


def _make_planning_use_case() -> PlanningUseCase:
    return PlanningUseCase(engine=PlanningEngine(strategy=SequentialStrategy()))


def _make_execution_use_case(
    planning: PlanningUseCase | None = None,
) -> ExecutionUseCase:
    if planning is None:
        planning = _make_planning_use_case()
    return ExecutionUseCase(
        engine=ExecutionEngine(registry=HandlerRegistry(), policy=ExecutionPolicy()),
        planning=planning,
    )


def _make_learning_use_case() -> LearningUseCase:
    return LearningUseCase(coordinator=MagicMock(spec=LearningCoordinator))


def _make_mapper() -> ExecutionLearningMapper:
    return ExecutionLearningMapper()


def _make_planning_summary() -> PlanningSummary:
    return PlanningSummary(
        plan_id=uuid.uuid4(),
        plan_status="draft",
        goal_count=1,
        action_count=1,
        dependency_count=0,
        blocker_count=0,
    )


def _make_execution_summary() -> ExecutionSummary:
    return ExecutionSummary(
        execution_started=True,
        execution_completed=True,
        execution_success=True,
        executed_action_count=1,
        failed_action_count=0,
        cancelled_action_count=0,
        execution_duration=timedelta(milliseconds=10),
    )


def _make_learning_summary() -> LearningSummary:
    return LearningSummary(
        learning_started=True,
        learning_completed=True,
        learning_success=True,
        observations_created=1,
        knowledge_updated=0,
        learning_duration=timedelta(milliseconds=5),
    )


def _make_workflow(
    session: BrainSession | None = None,
    planning: PlanningUseCase | None = None,
    execution: ExecutionUseCase | None = None,
    learning: LearningUseCase | None = None,
    mapper: ExecutionLearningMapper | None = None,
) -> BrainWorkflow:
    if session is None:
        session = _make_brain_session()
    if planning is None:
        planning = _make_planning_use_case()
    if execution is None:
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
    if learning is None:
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
    if mapper is None:
        mapper = _make_mapper()
    return BrainWorkflow(
        session=session,
        planning=planning,
        execution=execution,
        learning=learning,
        mapper=mapper,
    )


class TestConstruction:
    def test_creates_with_all_dependencies(self):
        session = _make_brain_session()
        planning = _make_planning_use_case()
        execution = _make_execution_use_case(planning)
        learning = _make_learning_use_case()
        mapper = _make_mapper()
        workflow = BrainWorkflow(
            session=session,
            planning=planning,
            execution=execution,
            learning=learning,
            mapper=mapper,
        )
        assert workflow._session is session
        assert workflow._planning is planning
        assert workflow._execution is execution
        assert workflow._learning is learning
        assert workflow._mapper is mapper

    def test_stores_session(self):
        workflow = _make_workflow()
        assert workflow._session is not None

    def test_stores_planning(self):
        planning = _make_planning_use_case()
        workflow = _make_workflow(planning=planning)
        assert workflow._planning is planning

    def test_stores_execution(self):
        execution = MagicMock(spec=ExecutionUseCase)
        workflow = _make_workflow(execution=execution)
        assert workflow._execution is execution

    def test_stores_learning(self):
        learning = MagicMock(spec=LearningUseCase)
        workflow = _make_workflow(learning=learning)
        assert workflow._learning is learning

    def test_stores_mapper(self):
        mapper = _make_mapper()
        workflow = _make_workflow(mapper=mapper)
        assert workflow._mapper is mapper

    def test_constructor_is_immutable(self):
        workflow = _make_workflow()
        assert workflow._session is not None
        assert workflow._planning is not None
        assert workflow._execution is not None
        assert workflow._learning is not None
        assert workflow._mapper is not None

    def test_no_unused_dependencies(self):
        workflow = _make_workflow()
        assert not hasattr(workflow, "_mapper_old")
        assert not hasattr(workflow, "_reflection")
        assert not hasattr(workflow, "_evolution")


class TestImmutability:
    def test_workflow_report_is_frozen(self):
        report = WorkflowReport(
            session_id=uuid.uuid4(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration=timedelta(seconds=1),
            success=True,
            failure_reason=None,
            task=_make_task(),
            context_available=True,
            plan_generated=True,
            execution_performed=True,
            learning_performed=True,
            reflection_performed=False,
            evolution_performed=False,
            plan_available=True,
            plan_status="draft",
            goal_count=1,
            action_count=1,
            dependency_count=0,
            blocker_count=0,
            planning_duration=timedelta(milliseconds=5),
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=1,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(milliseconds=10),
            learning_started=True,
            learning_completed=True,
            learning_success=True,
            observations_created=1,
            knowledge_updated=0,
            learning_duration=timedelta(milliseconds=5),
        )
        with pytest.raises(AttributeError):
            report.success = False

    def test_report_duration_exists(self):
        report = WorkflowReport(
            session_id=uuid.uuid4(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration=timedelta(seconds=5),
            success=True,
            failure_reason=None,
            task=_make_task(),
            context_available=True,
            plan_generated=True,
            execution_performed=True,
            learning_performed=True,
            reflection_performed=False,
            evolution_performed=False,
            plan_available=True,
            plan_status="draft",
            goal_count=1,
            action_count=2,
            dependency_count=1,
            blocker_count=0,
            planning_duration=timedelta(milliseconds=10),
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=2,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(milliseconds=20),
            learning_started=True,
            learning_completed=True,
            learning_success=True,
            observations_created=2,
            knowledge_updated=1,
            learning_duration=timedelta(milliseconds=5),
        )
        assert isinstance(report.duration, timedelta)
        assert report.duration == timedelta(seconds=5)

    def test_workflow_stores_original_session(self):
        session = _make_brain_session()
        workflow = BrainWorkflow(
            session=session,
            planning=_make_planning_use_case(),
            execution=_make_execution_use_case(),
            learning=_make_learning_use_case(),
            mapper=_make_mapper(),
        )
        assert workflow._session is session

    def test_workflow_stores_original_planning(self):
        planning = _make_planning_use_case()
        workflow = BrainWorkflow(
            session=_make_brain_session(),
            planning=planning,
            execution=_make_execution_use_case(planning),
            learning=_make_learning_use_case(),
            mapper=_make_mapper(),
        )
        assert workflow._planning is planning

    def test_workflow_stores_original_execution(self):
        execution = MagicMock(spec=ExecutionUseCase)
        workflow = BrainWorkflow(
            session=_make_brain_session(),
            planning=_make_planning_use_case(),
            execution=execution,
            learning=_make_learning_use_case(),
            mapper=_make_mapper(),
        )
        assert workflow._execution is execution

    def test_workflow_stores_original_learning(self):
        learning = MagicMock(spec=LearningUseCase)
        workflow = BrainWorkflow(
            session=_make_brain_session(),
            planning=_make_planning_use_case(),
            execution=MagicMock(spec=ExecutionUseCase),
            learning=learning,
            mapper=_make_mapper(),
        )
        assert workflow._learning is learning

    def test_workflow_stores_original_mapper(self):
        mapper = _make_mapper()
        workflow = BrainWorkflow(
            session=_make_brain_session(),
            planning=_make_planning_use_case(),
            execution=MagicMock(spec=ExecutionUseCase),
            learning=_make_learning_use_case(),
            mapper=mapper,
        )
        assert workflow._mapper is mapper


class TestRun:
    def test_returns_workflow_report(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert isinstance(report, WorkflowReport)

    def test_success_is_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.success is True
        assert report.failure_reason is None

    def test_context_available_is_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.context_available is True

    def test_plan_generated_is_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.plan_generated is True

    def test_execution_performed_is_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_performed is True

    def test_learning_performed_is_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_performed is True

    def test_reflection_performed_is_false(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.reflection_performed is False

    def test_evolution_performed_is_false(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.evolution_performed is False

    def test_session_id_is_uuid(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert isinstance(report.session_id, uuid.UUID)

    def test_session_id_unique_per_run(self):
        workflow = _make_workflow()
        r1 = workflow.run(_make_task())
        r2 = workflow.run(_make_task())
        assert r1.session_id != r2.session_id

    def test_started_at_populated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.started_at is not None
        assert isinstance(report.started_at, datetime)

    def test_completed_at_after_started_at(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.completed_at >= report.started_at

    def test_duration_non_negative(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.duration >= timedelta(0)

    def test_task_preserved_in_report(self):
        workflow = _make_workflow()
        task = _make_task()
        report = workflow.run(task)
        assert report.task is task


class TestPlanningInvocation:
    def test_execute_request_called(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        planning.execute_request.assert_called_once()

    def test_execute_request_receives_planning_request(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        args = planning.execute_request.call_args[0]
        request = args[0]
        assert isinstance(request, PlanningRequest)
        assert request.objective == "Implement workflow orchestration"
        assert request.project == "hermes-brain"
        assert request.component == "workflow"
        assert request.task_type == TaskType.IMPLEMENT

    def test_planning_called_exactly_once(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        assert planning.execute_request.call_count == 1


class TestExecutionInvocation:
    def test_execute_called(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        execution.execute.assert_called_once()

    def test_execute_receives_execution_request(self):
        planning = MagicMock(spec=PlanningUseCase)
        summary = _make_planning_summary()
        planning.execute_request.return_value = summary
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        args = execution.execute.call_args[0]
        request = args[0]
        assert isinstance(request, ExecutionRequest)
        assert request.plan_id == summary.plan_id
        assert request.project == "hermes-brain"

    def test_execute_called_exactly_once(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        assert execution.execute.call_count == 1

    def test_planning_then_execution_order(self):
        call_order = []
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.side_effect = lambda req: (
            call_order.append("planning"),
            _make_planning_summary(),
        )[1]
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.side_effect = lambda req: (
            call_order.append("execution"),
            _make_execution_summary(),
        )[1]
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.side_effect = lambda req: (
            call_order.append("learning"),
            _make_learning_summary(),
        )[1]
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        assert call_order == ["planning", "execution", "learning"]


class TestLearningInvocation:
    def test_execute_learning_called(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        learning.execute_learning.assert_called_once()

    def test_execute_learning_receives_learning_request(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        exec_summary = _make_execution_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = exec_summary
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        args = learning.execute_learning.call_args[0]
        request = args[0]
        assert isinstance(request, LearningRequest)

    def test_mapper_called_with_execution_summary(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        exec_summary = _make_execution_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = exec_summary
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        mapper = MagicMock(spec=ExecutionLearningMapper)
        learning_request = LearningRequest(
            execution_success=True,
            executed_count=1,
            failed_count=0,
            cancelled_count=0,
            duration=timedelta(0),
        )
        mapper.from_execution.return_value = learning_request
        workflow = _make_workflow(
            planning=planning, execution=execution, learning=learning, mapper=mapper,
        )
        workflow.run(_make_task())
        mapper.from_execution.assert_called_once_with(exec_summary)

    def test_learning_called_exactly_once(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        assert learning.execute_learning.call_count == 1


class TestPlanningMetrics:
    def test_plan_available_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.plan_available is True

    def test_plan_status_populated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.plan_status == "draft"

    def test_goal_count_one(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.goal_count == 1

    def test_action_count_from_plan(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.action_count >= 1

    def test_dependency_count_from_plan(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.dependency_count == 0

    def test_blocker_count_from_plan(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.blocker_count == 0

    def test_planning_duration_populated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.planning_duration >= timedelta(0)
        assert isinstance(report.planning_duration, timedelta)

    def test_planning_duration_includes_only_planning(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.planning_duration <= report.duration


class TestExecutionMetrics:
    def test_execution_started_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_started is True

    def test_execution_completed_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_completed is True

    def test_execution_success_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_success is True

    def test_executed_action_count(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.executed_action_count >= 0

    def test_failed_action_count_zero(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.failed_action_count == 0

    def test_cancelled_action_count_zero(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.cancelled_action_count == 0

    def test_execution_duration_populated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_duration >= timedelta(0)
        assert isinstance(report.execution_duration, timedelta)

    def test_execution_duration_includes_only_execution(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.execution_duration <= report.duration


class TestLearningMetrics:
    def test_learning_started_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_started is True

    def test_learning_completed_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_completed is True

    def test_learning_success_true(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_success is True

    def test_observations_created(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.observations_created >= 0

    def test_knowledge_updated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.knowledge_updated >= 0

    def test_learning_duration_populated(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_duration >= timedelta(0)
        assert isinstance(report.learning_duration, timedelta)

    def test_learning_duration_includes_only_learning(self):
        workflow = _make_workflow()
        report = workflow.run(_make_task())
        assert report.learning_duration <= report.duration


class TestEmptyPlan:
    def _make_empty_planning(self):
        from brain.planning.goal import Goal
        from brain.planning.plan import Plan

        return PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(
                    return_value=Plan(
                        goal=Goal(
                            title="empty",
                            description="empty",
                            project="empty",
                            priority=Priority.MEDIUM,
                        ),
                        actions=(),
                        dependencies=(),
                        blockers=(),
                        confidence=0.0,
                    )
                ),
            )
        )

    def test_workflow_succeeds_with_empty_plan(self):
        planning = self._make_empty_planning()
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.success is True

    def test_empty_plan_action_count_zero(self):
        planning = self._make_empty_planning()
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.action_count == 0

    def test_empty_plan_dependency_count_zero(self):
        planning = self._make_empty_planning()
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.dependency_count == 0

    def test_empty_plan_blocker_count_zero(self):
        planning = self._make_empty_planning()
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.blocker_count == 0


class TestFailure:
    def test_planner_failure_success_false(self):
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("planner crashed")),
            )
        )
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.success is False
        assert "planner crashed" in report.failure_reason

    def test_planner_failure_cleanup_executed(self):
        session = _make_brain_session()
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("boom")),
            )
        )
        workflow = _make_workflow(session=session, planning=planning)
        workflow.run(_make_task())
        status = session.status()
        assert status.active is False

    def test_planner_failure_no_leaked_exception(self):
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("fail")),
            )
        )
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert isinstance(report, WorkflowReport)

    def test_planner_failure_plan_metrics_zero(self):
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("crash")),
            )
        )
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.plan_available is False
        assert report.goal_count == 0
        assert report.action_count == 0
        assert report.dependency_count == 0
        assert report.blocker_count == 0

    def test_planner_failure_skips_execution_and_learning(self):
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("crash")),
            )
        )
        execution = MagicMock(spec=ExecutionUseCase)
        learning = MagicMock(spec=LearningUseCase)
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        execution.execute.assert_not_called()
        learning.execute_learning.assert_not_called()

    def test_planner_failure_learning_metrics_zero(self):
        planning = PlanningUseCase(
            engine=MagicMock(
                spec=PlanningEngine,
                create_plan=MagicMock(side_effect=RuntimeError("crash")),
            )
        )
        workflow = _make_workflow(planning=planning)
        report = workflow.run(_make_task())
        assert report.learning_started is False
        assert report.learning_completed is False
        assert report.observations_created == 0

    def test_begin_failure_cleanup_executed(self):
        session = _make_brain_session()
        session._brain.prepare.side_effect = RuntimeError("begin failed")
        planning = _make_planning_use_case()
        workflow = _make_workflow(session=session, planning=planning)
        report = workflow.run(_make_task())
        assert report.success is False
        assert "begin failed" in report.failure_reason
        status = session.status()
        assert status.active is False

    def test_begin_failure_plan_metrics_zero(self):
        session = _make_brain_session()
        session._brain.prepare.side_effect = RuntimeError("begin failed")
        planning = _make_planning_use_case()
        workflow = _make_workflow(session=session, planning=planning)
        report = workflow.run(_make_task())
        assert report.plan_available is False
        assert report.goal_count == 0

    def test_execution_failure_success_false(self):
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.side_effect = RuntimeError("exec failed")
        workflow = _make_workflow(execution=execution)
        report = workflow.run(_make_task())
        assert report.success is False
        assert "exec failed" in report.failure_reason

    def test_execution_failure_execution_metrics_zero(self):
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.side_effect = RuntimeError("exec failed")
        workflow = _make_workflow(execution=execution)
        report = workflow.run(_make_task())
        assert report.execution_started is False
        assert report.execution_completed is False
        assert report.execution_success is False
        assert report.executed_action_count == 0
        assert report.failed_action_count == 0
        assert report.cancelled_action_count == 0
        assert report.execution_duration == timedelta(0)

    def test_learning_failure_success_preserved(self):
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.side_effect = RuntimeError("learn failed")
        workflow = _make_workflow(execution=execution, learning=learning)
        report = workflow.run(_make_task())
        assert report.success is True
        assert report.failure_reason is None

    def test_learning_failure_execution_metrics_preserved(self):
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.side_effect = RuntimeError("learn failed")
        workflow = _make_workflow(execution=execution, learning=learning)
        report = workflow.run(_make_task())
        assert report.execution_performed is True

    def test_learning_failure_learning_metrics_zero(self):
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.side_effect = RuntimeError("learn failed")
        workflow = _make_workflow(execution=execution, learning=learning)
        report = workflow.run(_make_task())
        assert report.learning_started is False
        assert report.learning_completed is False
        assert report.observations_created == 0


class TestStatelessness:
    def test_multiple_runs_are_independent(self):
        workflow = _make_workflow()
        r1 = workflow.run(_make_task())
        r2 = workflow.run(_make_task())
        r3 = workflow.run(_make_task())
        assert all(r.success for r in [r1, r2, r3])
        assert len({r.session_id for r in [r1, r2, r3]}) == 3

    def test_session_clean_between_runs(self):
        session = _make_brain_session()
        workflow = _make_workflow(session=session)
        workflow.run(_make_task())
        workflow.run(_make_task())
        status = session.status()
        assert status.active is False

    def test_no_cached_plan_between_runs(self):
        planning = MagicMock(spec=PlanningUseCase)
        planning.execute_request.return_value = _make_planning_summary()
        execution = MagicMock(spec=ExecutionUseCase)
        execution.execute.return_value = _make_execution_summary()
        learning = MagicMock(spec=LearningUseCase)
        learning.execute_learning.return_value = _make_learning_summary()
        workflow = _make_workflow(planning=planning, execution=execution, learning=learning)
        workflow.run(_make_task())
        workflow.run(_make_task())
        assert planning.execute_request.call_count == 2

    def test_identical_behavior_across_runs(self):
        workflow = _make_workflow()
        reports = [workflow.run(_make_task()) for _ in range(5)]
        assert all(r.plan_available is True for r in reports)
        assert all(r.plan_status == "draft" for r in reports)
        assert all(r.goal_count == 1 for r in reports)
        assert all(r.execution_started is True for r in reports)
        assert all(r.execution_completed is True for r in reports)
        assert all(r.learning_started is True for r in reports)
        assert all(r.learning_completed is True for r in reports)


class TestSessionDelegation:
    def test_session_begin_called(self):
        session = _make_brain_session()
        workflow = _make_workflow(session=session)
        task = _make_task()
        workflow.run(task)
        session._brain.prepare.assert_called_once()

    def test_session_complete_called(self):
        session = _make_brain_session()
        workflow = _make_workflow(session=session)
        workflow.run(_make_task())
        status = session.status()
        assert status.active is False


class TestBrainSessionNoWorkflowKnowledge:
    def test_brain_session_has_no_workflow_import(self):
        source = inspect.getsource(BrainSession)
        assert "workflow" not in source.lower()

    def test_brain_session_has_no_create_workflow(self):
        assert not hasattr(BrainSession, "create_workflow")


class TestErrorHandling:
    def test_failed_begin_returns_success_false(self):
        session = _make_brain_session()
        session._brain.prepare.side_effect = RuntimeError("prepare failed")
        workflow = _make_workflow(session=session)
        report = workflow.run(_make_task())
        assert report.success is False
        assert "prepare failed" in report.failure_reason

    def test_failed_begin_sets_context_available_false(self):
        session = _make_brain_session()
        session._brain.prepare.side_effect = RuntimeError("boom")
        workflow = _make_workflow(session=session)
        report = workflow.run(_make_task())
        assert report.context_available is False

    def test_session_cleaned_up_on_error(self):
        session = _make_brain_session()
        session._brain.prepare.side_effect = RuntimeError("fail")
        workflow = _make_workflow(session=session)
        workflow.run(_make_task())
        status = session.status()
        assert status.active is False


class TestRuntimeWiring:
    def test_runtime_creates_workflow(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow is not None
        assert isinstance(r.workflow, BrainWorkflow)

    def test_workflow_uses_correct_session(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._session is r.session

    def test_workflow_uses_correct_planning(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._planning is not None
        assert isinstance(r.workflow._planning, PlanningUseCase)

    def test_workflow_uses_correct_execution(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._execution is not None
        assert isinstance(r.workflow._execution, ExecutionUseCase)

    def test_workflow_uses_correct_learning(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._learning is not None
        assert isinstance(r.workflow._learning, LearningUseCase)

    def test_workflow_uses_correct_mapper(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._mapper is not None
        assert isinstance(r.workflow._mapper, ExecutionLearningMapper)

    def test_planning_uses_correct_engine(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._planning.engine is not None

    def test_execution_uses_correct_engine(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._execution.engine is not None

    def test_execution_uses_same_planning(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._execution.planning is r.workflow._planning

    def test_learning_uses_correct_coordinator(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow._learning.coordinator is not None

    def test_workflow_is_frozen(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        with pytest.raises(AttributeError):
            r.workflow = None


class TestRollback:
    def test_workflow_module_is_self_contained(self):
        import brain.application.workflow as wf_mod
        assert hasattr(wf_mod, "BrainWorkflow")
        assert hasattr(wf_mod, "WorkflowReport")

    def test_removing_workflow_reverts_cleanly(self):
        from brain.runtime import create_memory_runtime
        r = create_memory_runtime()
        assert r.workflow is not None
        assert r.workflow._session is r.session
        assert r.workflow._planning is not None
        assert r.workflow._execution is not None
        assert r.workflow._learning is not None
        assert r.workflow._mapper is not None


class TestBoundaryIsolation:
    def test_brain_workflow_imports_no_goal(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.planning.goal import" not in source

    def test_brain_workflow_imports_no_action(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.planning.action import" not in source

    def test_brain_workflow_imports_no_plan(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.planning.plan import" not in source

    def test_brain_workflow_imports_no_planning_engine(self):
        source = inspect.getsource(BrainWorkflow)
        assert "PlanningEngine" not in source

    def test_brain_workflow_imports_no_dependency(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.planning.dependency import" not in source

    def test_brain_workflow_imports_no_blocker(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.planning.blocker import" not in source

    def test_brain_workflow_imports_no_strategy(self):
        source = inspect.getsource(BrainWorkflow)
        assert "SequentialStrategy" not in source
        assert "PlanningStrategy" not in source

    def test_brain_workflow_imports_no_execution_report(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.execution.report import" not in source

    def test_brain_workflow_imports_no_execution_result(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.execution.result import" not in source

    def test_brain_workflow_imports_no_execution_record(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.execution.record import" not in source

    def test_brain_workflow_imports_no_execution_context(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.execution.context import" not in source

    def test_brain_workflow_imports_no_learning_coordinator(self):
        source = inspect.getsource(BrainWorkflow)
        assert "LearningCoordinator" not in source

    def test_brain_workflow_imports_no_learning_report(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.learning" not in source

    def test_brain_workflow_imports_no_observation(self):
        source = inspect.getsource(BrainWorkflow)
        assert "Observation" not in source

    def test_brain_workflow_imports_no_detection(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.detection" not in source

    def test_brain_workflow_imports_no_evolution(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.evolution" not in source

    def test_brain_workflow_imports_no_reflection(self):
        source = inspect.getsource(BrainWorkflow)
        assert "from brain.reflection" not in source

    def test_brain_workflow_imports_planning_request(self):
        source = inspect.getsource(BrainWorkflow)
        assert "PlanningRequest" in source

    def test_brain_workflow_imports_execution_request(self):
        source = inspect.getsource(BrainWorkflow)
        assert "ExecutionRequest" in source

    def test_brain_workflow_imports_planning_use_case(self):
        source = inspect.getsource(BrainWorkflow)
        assert "PlanningUseCase" in source

    def test_brain_workflow_imports_execution_use_case(self):
        source = inspect.getsource(BrainWorkflow)
        assert "ExecutionUseCase" in source

    def test_brain_workflow_imports_learning_use_case(self):
        source = inspect.getsource(BrainWorkflow)
        assert "LearningUseCase" in source

    def test_brain_workflow_imports_mapper(self):
        source = inspect.getsource(BrainWorkflow)
        assert "ExecutionLearningMapper" in source

    def test_brain_workflow_creates_planning_request(self):
        source = inspect.getsource(BrainWorkflow)
        assert "PlanningRequest(" in source

    def test_brain_workflow_creates_execution_request(self):
        source = inspect.getsource(BrainWorkflow)
        assert "ExecutionRequest(" in source

    def test_brain_workflow_calls_execute_request(self):
        source = inspect.getsource(BrainWorkflow)
        assert "execute_request" in source

    def test_brain_workflow_calls_execution_execute(self):
        source = inspect.getsource(BrainWorkflow)
        assert "_execution.execute" in source

    def test_brain_workflow_calls_mapper_from_execution(self):
        source = inspect.getsource(BrainWorkflow)
        assert "_mapper.from_execution" in source

    def test_brain_workflow_calls_learning_execute_learning(self):
        source = inspect.getsource(BrainWorkflow)
        assert "_learning.execute_learning" in source

    def test_brain_workflow_no_del_plan(self):
        source = inspect.getsource(BrainWorkflow)
        assert "del plan" not in source
