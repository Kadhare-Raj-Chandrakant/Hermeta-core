import logging
import uuid
from datetime import datetime, timedelta, timezone

from brain.adapter.models import AdapterTask
from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.brain_session import BrainSession
from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.models import ExecutionRequest, PlanningRequest
from brain.application.usecases.planning import PlanningUseCase
from brain.application.workflow.report import WorkflowReport
from brain.domain.task import Priority, Task

_ZERO_DURATION = timedelta(0)

logger = logging.getLogger(__name__)

_DEFAULT_LEARNING_SUMMARY = {
    "learning_started": False,
    "learning_completed": False,
    "learning_success": False,
    "observations_created": 0,
    "knowledge_updated": 0,
    "learning_duration": _ZERO_DURATION,
}


class BrainWorkflow:
    def __init__(
        self,
        session: BrainSession,
        planning: PlanningUseCase,
        execution: ExecutionUseCase,
        learning: LearningUseCase,
        mapper: ExecutionLearningMapper,
    ) -> None:
        self._session = session
        self._planning = planning
        self._execution = execution
        self._learning = learning
        self._mapper = mapper

    def run(self, task: AdapterTask) -> WorkflowReport:
        session_id = uuid.uuid4()
        started_at = datetime.now(timezone.utc)
        try:
            domain_task = Task(
                task_type=task.task_type,
                project=task.project,
                component=task.component,
                objective=task.objective,
                constraints=(),
                priority=Priority.MEDIUM,
            )
            self._session.begin(domain_task)

            planning_started = datetime.now(timezone.utc)
            request = PlanningRequest(
                task_type=task.task_type,
                project=task.project,
                component=task.component,
                objective=task.objective,
            )
            planning_summary = self._planning.execute_request(request)
            planning_completed = datetime.now(timezone.utc)
            planning_duration = planning_completed - planning_started

            execution_started_at = datetime.now(timezone.utc)
            exec_request = ExecutionRequest(
                plan_id=planning_summary.plan_id,
                project=task.project,
            )
            execution_summary = self._execution.execute(exec_request)
            execution_completed_at = datetime.now(timezone.utc)
            execution_duration = execution_completed_at - execution_started_at

            learning_started_at = datetime.now(timezone.utc)
            learning_request = self._mapper.from_execution(execution_summary)
            try:
                learning_summary = self._learning.execute_learning(learning_request)
            except (ValueError, KeyError) as exc:
                logger.warning("Learning phase rejected by domain validation: %s", exc)
                learning_summary = None
            except Exception:
                logger.exception("Unexpected infrastructure error during learning phase")
                learning_summary = None
            learning_completed_at = datetime.now(timezone.utc)
            learning_duration = learning_completed_at - learning_started_at

            self._session.complete()
            completed_at = datetime.now(timezone.utc)

            if learning_summary is not None:
                return WorkflowReport(
                    session_id=session_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration=completed_at - started_at,
                    success=True,
                    failure_reason=None,
                    task=task,
                    context_available=True,
                    plan_generated=True,
                    execution_performed=True,
                    learning_performed=True,
                    reflection_performed=False,
                    evolution_performed=False,
                    plan_available=True,
                    plan_status=planning_summary.plan_status,
                    goal_count=planning_summary.goal_count,
                    action_count=planning_summary.action_count,
                    dependency_count=planning_summary.dependency_count,
                    blocker_count=planning_summary.blocker_count,
                    planning_duration=planning_duration,
                    execution_started=execution_summary.execution_started,
                    execution_completed=execution_summary.execution_completed,
                    execution_success=execution_summary.execution_success,
                    executed_action_count=execution_summary.executed_action_count,
                    failed_action_count=execution_summary.failed_action_count,
                    cancelled_action_count=execution_summary.cancelled_action_count,
                    execution_duration=execution_duration,
                    learning_started=learning_summary.learning_started,
                    learning_completed=learning_summary.learning_completed,
                    learning_success=learning_summary.learning_success,
                    observations_created=learning_summary.observations_created,
                    knowledge_updated=learning_summary.knowledge_updated,
                    learning_duration=learning_duration,
                )

            return WorkflowReport(
                session_id=session_id,
                started_at=started_at,
                completed_at=completed_at,
                duration=completed_at - started_at,
                success=True,
                failure_reason=None,
                task=task,
                context_available=True,
                plan_generated=True,
                execution_performed=True,
                learning_performed=False,
                reflection_performed=False,
                evolution_performed=False,
                plan_available=True,
                plan_status=planning_summary.plan_status,
                goal_count=planning_summary.goal_count,
                action_count=planning_summary.action_count,
                dependency_count=planning_summary.dependency_count,
                blocker_count=planning_summary.blocker_count,
                planning_duration=planning_duration,
                execution_started=execution_summary.execution_started,
                execution_completed=execution_summary.execution_completed,
                execution_success=execution_summary.execution_success,
                executed_action_count=execution_summary.executed_action_count,
                failed_action_count=execution_summary.failed_action_count,
                cancelled_action_count=execution_summary.cancelled_action_count,
                execution_duration=execution_duration,
                **_DEFAULT_LEARNING_SUMMARY,
            )
        except Exception as exc:
            try:
                self._session.complete()
            except RuntimeError:
                pass
            completed_at = datetime.now(timezone.utc)
            return WorkflowReport(
                session_id=session_id,
                started_at=started_at,
                completed_at=completed_at,
                duration=completed_at - started_at,
                success=False,
                failure_reason=str(exc),
                task=task,
                context_available=False,
                plan_generated=False,
                execution_performed=False,
                learning_performed=False,
                reflection_performed=False,
                evolution_performed=False,
                plan_available=False,
                plan_status="",
                goal_count=0,
                action_count=0,
                dependency_count=0,
                blocker_count=0,
                planning_duration=_ZERO_DURATION,
                execution_started=False,
                execution_completed=False,
                execution_success=False,
                executed_action_count=0,
                failed_action_count=0,
                cancelled_action_count=0,
                execution_duration=_ZERO_DURATION,
                **_DEFAULT_LEARNING_SUMMARY,
            )
