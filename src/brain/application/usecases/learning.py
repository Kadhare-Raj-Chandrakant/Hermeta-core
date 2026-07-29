from dataclasses import dataclass
from datetime import datetime, timezone

from brain.application.usecases.models import LearningRequest, LearningSummary
from brain.detection.observation import Observation
from brain.execution.report import ExecutionReport
from brain.learning.coordinator import LearningCoordinator
from brain.learning.report import LearningReport


@dataclass(frozen=True)
class LearningUseCase:
    coordinator: LearningCoordinator

    def execute(
        self, observations: tuple[Observation, ...]
    ) -> LearningReport:
        return self.coordinator.learn_from_observations(observations)

    def execute_from_execution(
        self, report: ExecutionReport
    ) -> LearningReport:
        return self.coordinator.learn_from_execution(report)

    def execute_learning(self, request: LearningRequest) -> LearningSummary:
        start = datetime.now(timezone.utc)

        observations = self._request_to_observations(request)
        report = self.coordinator.learn_from_observations(observations)

        end = datetime.now(timezone.utc)
        duration = end - start

        return LearningSummary(
            learning_started=True,
            learning_completed=True,
            learning_success=report.rejected == 0,
            observations_created=report.observations_processed,
            knowledge_updated=report.accepted,
            learning_duration=duration,
        )

    def _request_to_observations(
        self, request: LearningRequest
    ) -> tuple[Observation, ...]:
        if request.execution_success:
            content = (
                f"Execution completed successfully: "
                f"{request.executed_count} actions succeeded"
            )
        else:
            content = (
                f"Execution failed: {request.failed_count} of "
                f"{request.executed_count} actions failed"
            )

        metadata: list[tuple[str, str]] = [
            ("executed_count", str(request.executed_count)),
            ("failed_count", str(request.failed_count)),
            ("cancelled_count", str(request.cancelled_count)),
        ]

        return (
            Observation(
                source_type="execution",
                content=content,
                metadata=tuple(metadata),
            ),
        )
