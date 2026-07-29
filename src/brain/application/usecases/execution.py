from dataclasses import dataclass
from datetime import timedelta

from brain.application.usecases.models import ExecutionRequest, ExecutionSummary
from brain.application.usecases.planning import PlanningUseCase
from brain.execution.context import ExecutionContext
from brain.execution.executor import ExecutionEngine
from brain.execution.report import ExecutionReport


@dataclass(frozen=True)
class ExecutionUseCase:
    engine: ExecutionEngine
    planning: PlanningUseCase

    def execute(self, request: ExecutionRequest) -> ExecutionSummary:
        plan = self.planning.get_plan(request.plan_id)
        context = ExecutionContext(
            plan_id=request.plan_id,
            project=request.project,
            metadata=request.metadata,
        )
        report = self.engine.execute(plan, context)
        return self._summarize(report)

    def _summarize(self, report: ExecutionReport) -> ExecutionSummary:
        executed = len(report.results)
        succeeded = report.completed
        failed = report.failed
        cancelled = executed - succeeded - failed
        return ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=failed == 0,
            executed_action_count=executed,
            failed_action_count=failed,
            cancelled_action_count=cancelled,
            execution_duration=report.completed_at - report.started_at,
        )
