import uuid
from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.models import LearningRequest, LearningSummary
from brain.detection.observation import Observation
from brain.execution.report import ExecutionReport
from brain.learning.coordinator import LearningCoordinator
from brain.learning.report import LearningReport


def _make_coordinator() -> LearningCoordinator:
    return MagicMock(spec=LearningCoordinator)


def _make_observations() -> tuple[Observation, ...]:
    return (
        Observation(source_type="test", content="obs 1"),
        Observation(source_type="test", content="obs 2"),
    )


def _make_report() -> ExecutionReport:
    return MagicMock(spec=ExecutionReport)


def _make_learning_report(
    observations_processed: int = 2,
    candidates_detected: int = 0,
    accepted: int = 0,
    rejected: int = 0,
) -> LearningReport:
    return LearningReport(
        observations_processed=observations_processed,
        candidates_detected=candidates_detected,
        accepted=accepted,
        rejected=rejected,
        events_processed=accepted,
        reflection_findings=0,
        transitions_created=0,
        duration=timedelta(milliseconds=5),
    )


def _make_request(
    execution_success: bool = True,
    executed_count: int = 3,
    failed_count: int = 0,
    cancelled_count: int = 0,
) -> LearningRequest:
    return LearningRequest(
        execution_success=execution_success,
        executed_count=executed_count,
        failed_count=failed_count,
        cancelled_count=cancelled_count,
        duration=timedelta(seconds=2),
    )


class TestConstruction:
    def test_stores_coordinator(self):
        coord = _make_coordinator()
        use_case = LearningUseCase(coordinator=coord)
        assert use_case.coordinator is coord


class TestDelegation:
    def test_execute_delegates_to_learn_from_observations(self):
        coord = MagicMock(spec=LearningCoordinator)
        expected = MagicMock(spec=LearningReport)
        coord.learn_from_observations.return_value = expected

        use_case = LearningUseCase(coordinator=coord)
        observations = _make_observations()

        result = use_case.execute(observations)

        coord.learn_from_observations.assert_called_once_with(observations)
        assert result is expected

    def test_execute_from_execution_delegates(self):
        coord = MagicMock(spec=LearningCoordinator)
        expected = MagicMock(spec=LearningReport)
        coord.learn_from_execution.return_value = expected

        use_case = LearningUseCase(coordinator=coord)
        report = _make_report()

        result = use_case.execute_from_execution(report)

        coord.learn_from_execution.assert_called_once_with(report)
        assert result is expected

    def test_execute_returns_coordinator_result(self):
        coord = MagicMock(spec=LearningCoordinator)
        sentinel = MagicMock(spec=LearningReport)
        coord.learn_from_observations.return_value = sentinel

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute(_make_observations())

        assert result is sentinel

    def test_arguments_forwarded_unchanged(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = MagicMock(spec=LearningReport)

        use_case = LearningUseCase(coordinator=coord)
        observations = _make_observations()

        use_case.execute(observations)

        coord.learn_from_observations.assert_called_once_with(observations)


class TestExecuteLearning:
    def test_returns_learning_summary(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert isinstance(result, LearningSummary)

    def test_calls_coordinator_with_observations(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        use_case.execute_learning(_make_request())

        coord.learn_from_observations.assert_called_once()
        args = coord.learn_from_observations.call_args[0]
        observations = args[0]
        assert isinstance(observations, tuple)
        assert len(observations) == 1
        assert isinstance(observations[0], Observation)

    def test_successful_execution_creates_observation(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        use_case.execute_learning(_make_request(execution_success=True))

        observations = coord.learn_from_observations.call_args[0][0]
        assert observations[0].source_type == "execution"
        assert "succeeded" in observations[0].content

    def test_failed_execution_creates_observation(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        use_case.execute_learning(
            _make_request(execution_success=False, executed_count=5, failed_count=2)
        )

        observations = coord.learn_from_observations.call_args[0][0]
        assert "failed" in observations[0].content
        assert "2 of 5" in observations[0].content

    def test_summary_learning_started_true(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.learning_started is True

    def test_summary_learning_completed_true(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.learning_completed is True

    def test_summary_success_when_no_rejections(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report(
            accepted=2, rejected=0
        )

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.learning_success is True

    def test_summary_failure_when_rejections(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report(
            accepted=1, rejected=1
        )

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.learning_success is False

    def test_summary_observations_created(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report(
            observations_processed=3
        )

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.observations_created == 3

    def test_summary_knowledge_updated(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report(
            accepted=5
        )

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.knowledge_updated == 5

    def test_summary_learning_duration_populated(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute_learning(_make_request())

        assert result.learning_duration >= timedelta(0)
        assert isinstance(result.learning_duration, timedelta)

    def test_coordinator_failure_propagates(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.side_effect = RuntimeError("boom")

        use_case = LearningUseCase(coordinator=coord)
        with pytest.raises(RuntimeError, match="boom"):
            use_case.execute_learning(_make_request())

    def test_observation_metadata_populated(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.return_value = _make_learning_report()

        use_case = LearningUseCase(coordinator=coord)
        use_case.execute_learning(
            _make_request(
                executed_count=10, failed_count=3, cancelled_count=1,
            )
        )

        observations = coord.learn_from_observations.call_args[0][0]
        metadata = dict(observations[0].metadata)
        assert metadata["executed_count"] == "10"
        assert metadata["failed_count"] == "3"
        assert metadata["cancelled_count"] == "1"


class TestStatelessness:
    def test_two_calls_produce_independent_results(self):
        coord = MagicMock(spec=LearningCoordinator)
        r1 = MagicMock(spec=LearningReport)
        r2 = MagicMock(spec=LearningReport)
        coord.learn_from_observations.side_effect = [r1, r2]

        use_case = LearningUseCase(coordinator=coord)
        observations = _make_observations()

        result1 = use_case.execute(observations)
        result2 = use_case.execute(observations)

        assert result1 is r1
        assert result2 is r2


class TestImmutability:
    def test_frozen(self):
        coord = _make_coordinator()
        use_case = LearningUseCase(coordinator=coord)
        with pytest.raises(AttributeError):
            use_case.coordinator = None


class TestNoHiddenLogic:
    def test_no_transformation(self):
        coord = MagicMock(spec=LearningCoordinator)
        sentinel = MagicMock(spec=LearningReport)
        coord.learn_from_observations.return_value = sentinel

        use_case = LearningUseCase(coordinator=coord)
        result = use_case.execute(_make_observations())

        assert result is sentinel

    def test_no_exception_swallowing(self):
        coord = MagicMock(spec=LearningCoordinator)
        coord.learn_from_observations.side_effect = RuntimeError("boom")

        use_case = LearningUseCase(coordinator=coord)
        with pytest.raises(RuntimeError, match="boom"):
            use_case.execute(_make_observations())
