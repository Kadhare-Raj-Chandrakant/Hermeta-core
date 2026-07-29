from datetime import datetime, timezone

from brain.execution.context import ExecutionContext
from brain.execution.errors import ActionExecutionError, NoHandlerError
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.observer import ExecutionObserver
from brain.execution.policy import ExecutionPolicy
from brain.execution.record import ExecutionRecord
from brain.execution.report import ExecutionReport
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.planning.plan import Plan


class ExecutionEngine:
    def __init__(
        self,
        registry: HandlerRegistry,
        policy: ExecutionPolicy,
        observers: tuple[ExecutionObserver, ...] = (),
    ) -> None:
        self._registry = registry
        self._policy = policy
        self._observers = observers

    def execute(self, plan: Plan, context: ExecutionContext) -> ExecutionReport:
        start = datetime.now(timezone.utc)
        results: list[ExecutionResult] = []

        for action in plan.actions:
            record = ExecutionRecord(
                action_id=action.id,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
            )

            for observer in self._observers:
                observer.on_started(record)

            try:
                handler = self._registry.find(action)
                result = handler.execute(action, context)
            except NoHandlerError:
                raise
            except Exception as e:
                end = datetime.now(timezone.utc)
                record = ExecutionRecord(
                    action_id=action.id,
                    status=ExecutionStatus.FAILED,
                    started_at=record.started_at,
                    completed_at=end,
                )
                result = ExecutionResult(
                    record=record,
                    success=False,
                    output="",
                    error=str(e),
                    duration=end - record.started_at,
                )

            results.append(result)

            for observer in self._observers:
                if result.success:
                    observer.on_completed(result)
                else:
                    observer.on_failed(result)

            if not result.success and self._policy.stop_on_failure:
                break

        end = datetime.now(timezone.utc)
        return ExecutionReport(
            plan_id=plan.id,
            results=tuple(results),
            started_at=start,
            completed_at=end,
        )
