from brain.detection.observation import Observation
from brain.execution.report import ExecutionReport
from brain.execution.result import ExecutionResult


class ExecutionFeedback:
    def to_observations(self, report: ExecutionReport) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        for result in report.results:
            metadata = self._build_metadata(report, result)
            content = self._build_content(result)

            observations.append(
                Observation(
                    source_type="execution",
                    content=content,
                    metadata=metadata,
                )
            )
        return tuple(observations)

    def _build_metadata(
        self, report: ExecutionReport, result: ExecutionResult
    ) -> tuple[tuple[str, str], ...]:
        meta: list[tuple[str, str]] = [
            ("plan_id", str(report.plan_id)),
            ("action_id", str(result.record.action_id)),
            ("status", result.record.status.value),
            ("duration_ms", str(int(result.duration.total_seconds() * 1000))),
        ]

        if result.output:
            meta.append(("output", result.output))

        if result.error:
            error_type = type(result.error).__name__ if hasattr(result.error, '__name__') else "Error"
            meta.append(("error_type", error_type))
            meta.append(("error_message", str(result.error)))

        return tuple(meta)

    def _build_content(self, result: ExecutionResult) -> str:
        status = result.record.status.value
        if result.success:
            output_preview = result.output[:120] if result.output else "success"
            return f"Action {status}: {output_preview}"
        elif result.error:
            error_preview = str(result.error)[:120]
            return f"Action {status}: {error_preview}"
        else:
            return f"Action {status}: no details"
