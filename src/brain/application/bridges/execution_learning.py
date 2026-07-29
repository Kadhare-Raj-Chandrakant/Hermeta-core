from brain.application.usecases.models import ExecutionSummary, LearningRequest


class ExecutionLearningMapper:
    def from_execution(self, summary: ExecutionSummary) -> LearningRequest:
        return LearningRequest(
            execution_success=summary.execution_success,
            executed_count=summary.executed_action_count,
            failed_count=summary.failed_action_count,
            cancelled_count=summary.cancelled_action_count,
            duration=summary.execution_duration,
        )
