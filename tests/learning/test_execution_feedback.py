import pytest

from brain.detection.observation import Observation
from brain.execution.report import ExecutionReport
from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.learning.execution_feedback import ExecutionFeedback
from datetime import datetime, timezone, timedelta


def _make_result(
    success: bool,
    output: str = "",
    error: str | None = None,
) -> ExecutionResult:
    now = datetime.now(timezone.utc)
    record = ExecutionRecord(
        action_id=__import__("uuid").uuid4(),
        status=ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED,
        started_at=now,
        completed_at=now,
    )
    return ExecutionResult(
        record=record,
        success=success,
        output=output,
        error=error,
        duration=timedelta(seconds=1.0),
    )


class TestExecutionFeedback:
    def test_success_produces_observation(self):
        feedback = ExecutionFeedback()
        result = _make_result(success=True, output="Deployed successfully")
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(result,),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        observations = feedback.to_observations(report)

        assert len(observations) == 1
        assert observations[0].source_type == "execution"
        assert "Deployed successfully" in observations[0].content

    def test_failure_produces_observation(self):
        feedback = ExecutionFeedback()
        result = _make_result(success=False, error="Connection timeout")
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(result,),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        observations = feedback.to_observations(report)

        assert len(observations) == 1
        assert observations[0].source_type == "execution"
        assert "Connection timeout" in observations[0].content

    def test_empty_report_produces_no_observations(self):
        feedback = ExecutionFeedback()
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        observations = feedback.to_observations(report)

        assert len(observations) == 0

    def test_mixed_results(self):
        feedback = ExecutionFeedback()
        r1 = _make_result(success=True, output="OK")
        r2 = _make_result(success=False, error="Failed")
        r3 = _make_result(success=True, output="Done")
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(r1, r2, r3),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        observations = feedback.to_observations(report)

        assert len(observations) == 3
        assert observations[0].source_type == "execution"
        assert "OK" in observations[0].content
        assert observations[1].source_type == "execution"
        assert "Failed" in observations[1].content
        assert observations[2].source_type == "execution"
        assert "Done" in observations[2].content

    def test_all_observations_are_valid(self):
        feedback = ExecutionFeedback()
        result = _make_result(success=True, output="Test")
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(result,),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        observations = feedback.to_observations(report)

        for obs in observations:
            assert isinstance(obs, Observation)
            assert obs.source_type
            assert obs.content

    def test_deterministic_conversion(self):
        feedback = ExecutionFeedback()
        result = _make_result(success=True, output="Same")
        report = ExecutionReport(
            plan_id=__import__("uuid").uuid4(),
            results=(result,),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        obs1 = feedback.to_observations(report)
        obs2 = feedback.to_observations(report)

        assert len(obs1) == len(obs2)
        assert obs1[0].source_type == obs2[0].source_type
        assert obs1[0].content == obs2[0].content
