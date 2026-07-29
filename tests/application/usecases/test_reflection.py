from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from brain.application.usecases.models import ReflectionRequest, ReflectionSummary
from brain.application.usecases.reflection import ReflectionUseCase
from brain.reflection.engine import ReflectionEngine
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport
from brain.reflection.type import ReflectionType
from brain.repositories.base import KnowledgeRepository


def _make_engine() -> ReflectionEngine:
    return MagicMock(spec=ReflectionEngine)


def _make_repository() -> KnowledgeRepository:
    return MagicMock(spec=KnowledgeRepository)


def _make_finding(
    reflection_type: ReflectionType = ReflectionType.DUPLICATE,
) -> ReflectionFinding:
    return ReflectionFinding(
        reflection_type=reflection_type,
        affected_versions=(),
        explanation="test finding",
        confidence=0.8,
    )


def _make_report(
    findings: tuple[ReflectionFinding, ...] = (),
    versions_checked: int = 0,
) -> ReflectionReport:
    return ReflectionReport(
        versions_checked=versions_checked,
        detectors_used=("DuplicateDetector",),
        findings=findings,
        duration=timedelta(milliseconds=5),
    )


def _make_request(
    scope: str = "all",
    project: str = "hermes-brain",
) -> ReflectionRequest:
    return ReflectionRequest(scope=scope, project=project)


class TestConstruction:
    def test_stores_engine(self):
        engine = _make_engine()
        repo = _make_repository()
        use_case = ReflectionUseCase(engine=engine, repository=repo)
        assert use_case.engine is engine

    def test_stores_repository(self):
        engine = _make_engine()
        repo = _make_repository()
        use_case = ReflectionUseCase(engine=engine, repository=repo)
        assert use_case.repository is repo


class TestExecute:
    def test_returns_reflection_summary(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert isinstance(result, ReflectionSummary)

    def test_calls_repository_list_all_versions(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        use_case.execute(_make_request())

        repo.list_all_versions.assert_called_once()

    def test_calls_engine_reflect_with_versions(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        versions = (MagicMock(), MagicMock())
        repo.list_all_versions.return_value = versions

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        use_case.execute(_make_request())

        engine.reflect.assert_called_once_with(versions)

    def test_summary_reflection_started_true(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.reflection_started is True

    def test_summary_reflection_completed_true(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.reflection_completed is True

    def test_summary_reflection_success_true(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.reflection_success is True

    def test_summary_finding_count(self):
        findings = (
            _make_finding(ReflectionType.DUPLICATE),
            _make_finding(ReflectionType.CONFLICT),
            _make_finding(ReflectionType.GAP),
        )
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=findings)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.finding_count == 3

    def test_summary_duplicate_count(self):
        findings = (
            _make_finding(ReflectionType.DUPLICATE),
            _make_finding(ReflectionType.DUPLICATE),
            _make_finding(ReflectionType.CONFLICT),
        )
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=findings)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.duplicate_count == 2

    def test_summary_conflict_count(self):
        findings = (_make_finding(ReflectionType.CONFLICT),)
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=findings)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.conflict_count == 1

    def test_summary_obsolete_count(self):
        findings = (_make_finding(ReflectionType.OBSOLETE),)
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=findings)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.obsolete_count == 1

    def test_summary_gap_count(self):
        findings = (_make_finding(ReflectionType.GAP),)
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=findings)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.gap_count == 1

    def test_summary_empty_findings(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report(findings=())
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.finding_count == 0
        assert result.duplicate_count == 0
        assert result.conflict_count == 0
        assert result.obsolete_count == 0
        assert result.gap_count == 0

    def test_summary_reflection_duration_populated(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.return_value = _make_report()
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result = use_case.execute(_make_request())

        assert result.reflection_duration >= timedelta(0)
        assert isinstance(result.reflection_duration, timedelta)

    def test_engine_failure_propagates(self):
        engine = MagicMock(spec=ReflectionEngine)
        engine.reflect.side_effect = RuntimeError("boom")
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        with pytest.raises(RuntimeError, match="boom"):
            use_case.execute(_make_request())

    def test_repository_failure_propagates(self):
        engine = MagicMock(spec=ReflectionEngine)
        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.side_effect = RuntimeError("repo down")

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        with pytest.raises(RuntimeError, match="repo down"):
            use_case.execute(_make_request())


class TestStatelessness:
    def test_two_calls_produce_independent_results(self):
        engine = MagicMock(spec=ReflectionEngine)
        r1 = _make_report(findings=(_make_finding(ReflectionType.DUPLICATE),))
        r2 = _make_report(findings=(_make_finding(ReflectionType.GAP),))
        engine.reflect.side_effect = [r1, r2]

        repo = MagicMock(spec=KnowledgeRepository)
        repo.list_all_versions.return_value = ()

        use_case = ReflectionUseCase(engine=engine, repository=repo)
        result1 = use_case.execute(_make_request())
        result2 = use_case.execute(_make_request())

        assert result1 is not result2
        assert result1.duplicate_count == 1
        assert result2.gap_count == 1


class TestImmutability:
    def test_frozen(self):
        engine = _make_engine()
        repo = _make_repository()
        use_case = ReflectionUseCase(engine=engine, repository=repo)
        with pytest.raises(AttributeError):
            use_case.engine = None

    def test_cannot_reassign_repository(self):
        engine = _make_engine()
        repo = _make_repository()
        use_case = ReflectionUseCase(engine=engine, repository=repo)
        with pytest.raises(AttributeError):
            use_case.repository = None
