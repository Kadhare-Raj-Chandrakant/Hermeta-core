from datetime import timedelta

import pytest

from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.usecases.models import ExecutionSummary, LearningRequest


class TestConstruction:
    def test_creates_without_dependencies(self):
        mapper = ExecutionLearningMapper()
        assert mapper is not None


class TestFromExecution:
    def test_returns_learning_request(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=3,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=5),
        )
        result = mapper.from_execution(summary)
        assert isinstance(result, LearningRequest)

    def test_maps_execution_success(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=3,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=5),
        )
        result = mapper.from_execution(summary)
        assert result.execution_success is True

    def test_maps_execution_failure(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=False,
            executed_action_count=5,
            failed_action_count=2,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=10),
        )
        result = mapper.from_execution(summary)
        assert result.execution_success is False

    def test_maps_executed_count(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=42,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=1),
        )
        result = mapper.from_execution(summary)
        assert result.executed_count == 42

    def test_maps_failed_count(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=False,
            executed_action_count=10,
            failed_action_count=7,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=1),
        )
        result = mapper.from_execution(summary)
        assert result.failed_count == 7

    def test_maps_cancelled_count(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=False,
            executed_action_count=10,
            failed_action_count=3,
            cancelled_action_count=2,
            execution_duration=timedelta(seconds=1),
        )
        result = mapper.from_execution(summary)
        assert result.cancelled_count == 2

    def test_maps_duration(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=1,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=99),
        )
        result = mapper.from_execution(summary)
        assert result.duration == timedelta(seconds=99)

    def test_frozen_output(self):
        mapper = ExecutionLearningMapper()
        summary = ExecutionSummary(
            execution_started=True,
            execution_completed=True,
            execution_success=True,
            executed_action_count=1,
            failed_action_count=0,
            cancelled_action_count=0,
            execution_duration=timedelta(seconds=1),
        )
        result = mapper.from_execution(summary)
        with pytest.raises(AttributeError):
            result.execution_success = False


class TestBoundaryIsolation:
    def test_no_engine_dependency(self):
        import inspect
        source = inspect.getsource(ExecutionLearningMapper)
        assert "Engine" not in source
        assert "engine" not in source

    def test_no_repository_dependency(self):
        import inspect
        source = inspect.getsource(ExecutionLearningMapper)
        assert "repository" not in source.lower()
        assert "Repository" not in source

    def test_no_coordinator_dependency(self):
        import inspect
        source = inspect.getsource(ExecutionLearningMapper)
        assert "coordinator" not in source.lower()
        assert "Coordinator" not in source

    def test_only_uses_application_dtos(self):
        import inspect
        source = inspect.getsource(ExecutionLearningMapper)
        assert "ExecutionSummary" in source
        assert "LearningRequest" in source

    def test_no_domain_model_imports(self):
        import inspect
        source = inspect.getsource(ExecutionLearningMapper)
        assert "from brain.detection" not in source
        assert "from brain.execution" not in source
        assert "from brain.learning" not in source
        assert "from brain.planning" not in source
