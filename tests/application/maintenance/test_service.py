from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from brain.application.maintenance.service import ReflectionMaintenanceService
from brain.application.usecases.models import ReflectionRequest, ReflectionSummary
from brain.application.usecases.reflection import ReflectionUseCase


def _make_use_case() -> ReflectionUseCase:
    return MagicMock(spec=ReflectionUseCase)


def _make_summary() -> ReflectionSummary:
    return ReflectionSummary(
        reflection_started=True,
        reflection_completed=True,
        reflection_success=True,
        reflection_duration=timedelta(milliseconds=10),
        finding_count=0,
        duplicate_count=0,
        conflict_count=0,
        obsolete_count=0,
        gap_count=0,
    )


def _make_request() -> ReflectionRequest:
    return ReflectionRequest(scope="all", project="hermes-brain")


class TestConstruction:
    def test_stores_reflection_use_case(self):
        use_case = _make_use_case()
        service = ReflectionMaintenanceService(reflection=use_case)
        assert service.reflection is use_case


class TestReflect:
    def test_returns_reflection_summary(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        use_case.execute.return_value = _make_summary()

        service = ReflectionMaintenanceService(reflection=use_case)
        result = service.reflect(_make_request())

        assert isinstance(result, ReflectionSummary)

    def test_delegates_to_use_case(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        use_case.execute.return_value = _make_summary()

        service = ReflectionMaintenanceService(reflection=use_case)
        service.reflect(_make_request())

        use_case.execute.assert_called_once()

    def test_passes_request_to_use_case(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        use_case.execute.return_value = _make_summary()

        service = ReflectionMaintenanceService(reflection=use_case)
        request = _make_request()
        service.reflect(request)

        use_case.execute.assert_called_once_with(request)

    def test_returns_use_case_result(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        sentinel = _make_summary()
        use_case.execute.return_value = sentinel

        service = ReflectionMaintenanceService(reflection=use_case)
        result = service.reflect(_make_request())

        assert result is sentinel

    def test_use_case_failure_propagates(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        use_case.execute.side_effect = RuntimeError("boom")

        service = ReflectionMaintenanceService(reflection=use_case)
        with pytest.raises(RuntimeError, match="boom"):
            service.reflect(_make_request())


class TestStatelessness:
    def test_multiple_calls_are_independent(self):
        use_case = MagicMock(spec=ReflectionUseCase)
        s1 = _make_summary()
        s2 = ReflectionSummary(
            reflection_started=True,
            reflection_completed=True,
            reflection_success=True,
            reflection_duration=timedelta(milliseconds=20),
            finding_count=3,
            duplicate_count=1,
            conflict_count=1,
            obsolete_count=0,
            gap_count=1,
        )
        use_case.execute.side_effect = [s1, s2]

        service = ReflectionMaintenanceService(reflection=use_case)
        result1 = service.reflect(_make_request())
        result2 = service.reflect(_make_request())

        assert result1 is not result2
        assert result1.finding_count == 0
        assert result2.finding_count == 3


class TestImmutability:
    def test_frozen(self):
        service = ReflectionMaintenanceService(reflection=_make_use_case())
        with pytest.raises(AttributeError):
            service.reflection = None


class TestBoundaryIsolation:
    def test_no_engine_import(self):
        import inspect
        source = inspect.getsource(ReflectionMaintenanceService)
        assert "ReflectionEngine" not in source

    def test_no_repository_import(self):
        import inspect
        source = inspect.getsource(ReflectionMaintenanceService)
        assert "Repository" not in source

    def test_only_uses_application_types(self):
        import inspect
        source = inspect.getsource(ReflectionMaintenanceService)
        assert "ReflectionUseCase" in source
        assert "ReflectionRequest" in source
        assert "ReflectionSummary" in source
