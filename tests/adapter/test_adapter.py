import uuid
from unittest.mock import MagicMock

import pytest

from brain.adapter.adapter import BrainAdapter
from brain.adapter.errors import AdapterError, AdapterNotReadyError
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.models import AdapterContext, AdapterLearning, AdapterTask
from brain.adapter.task_mapper import TaskMapper
from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence
from brain.services.compiler import ContextPackage


def _make_adapter_task(task_type: TaskType = TaskType.IMPLEMENT, **overrides) -> AdapterTask:
    defaults = dict(
        task_id=uuid.uuid4(),
        task_type=task_type,
        objective="Implement login",
        project="atlas",
        component="auth",
    )
    defaults.update(overrides)
    return AdapterTask(**defaults)


def _make_learning(**overrides) -> AdapterLearning:
    defaults = dict(
        task_id=uuid.uuid4(),
        knowledge_type="ARCHITECTURE",
        title="Auth Architecture",
        understanding="OAuth2 flow",
        confidence=0.9,
    )
    defaults.update(overrides)
    return AdapterLearning(**defaults)


def _make_context_package() -> ContextPackage:
    task = Task(
        task_type=TaskType.IMPLEMENT,
        project="atlas",
        component="auth",
        objective="test",
        constraints=(),
        priority=Priority.MEDIUM,
    )
    return ContextPackage(task=task, sections=())


def _make_version() -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=KnowledgeType.ARCHITECTURE,
        title="Auth",
        understanding="OAuth2",
        confidence=0.9,
    )


def _make_adapter(**overrides):
    session = overrides.pop("session", MagicMock())
    mapper = overrides.pop("mapper", TaskMapper())
    lifecycle = overrides.pop("lifecycle", AdapterLifecycle())
    session.begin.return_value = _make_context_package()
    session.learn.return_value = _make_version()
    return BrainAdapter(session=session, mapper=mapper, lifecycle=lifecycle), session


class TestStartTaskWithMapper:
    def test_uses_mapper(self) -> None:
        adapter, session = _make_adapter()
        task = _make_adapter_task(task_type=TaskType.DEBUG)
        adapter.start_task(task)

        called_task = session.begin.call_args[0][0]
        assert called_task.task_type == TaskType.DEBUG

    def test_mapper_translates_all_fields(self) -> None:
        adapter, session = _make_adapter()
        task = _make_adapter_task(
            task_type=TaskType.REFACTOR,
            project="hermes",
            component="api",
            objective="Refactor endpoints",
        )
        adapter.start_task(task)

        called_task = session.begin.call_args[0][0]
        assert called_task.task_type == TaskType.REFACTOR
        assert called_task.project == "hermes"
        assert called_task.component == "api"
        assert called_task.objective == "Refactor endpoints"

    def test_returns_adapter_context(self) -> None:
        adapter, _ = _make_adapter()
        task = _make_adapter_task()
        result = adapter.start_task(task)
        assert isinstance(result, AdapterContext)
        assert result.task_id == task.task_id


class TestLearnWithLifecycle:
    def test_requires_active_session(self) -> None:
        adapter, _ = _make_adapter()
        learning = _make_learning()
        with pytest.raises(AdapterNotReadyError, match="No active session"):
            adapter.learn(learning)

    def test_learn_when_active(self) -> None:
        adapter, session = _make_adapter()
        adapter.start_task(_make_adapter_task())
        learning = _make_learning()
        result = adapter.learn(learning)
        assert isinstance(result, KnowledgeVersion)
        session.learn.assert_called_once()
        called_candidate = session.learn.call_args[0][0]
        assert isinstance(called_candidate, KnowledgeCandidate)
        assert called_candidate.knowledge_type == KnowledgeType.ARCHITECTURE
        assert called_candidate.title == "Auth Architecture"


class TestCompleteWithLifecycle:
    def test_complete_requires_active(self) -> None:
        adapter, _ = _make_adapter()
        with pytest.raises(AdapterNotReadyError, match="No active session"):
            adapter.complete_task(uuid.uuid4())

    def test_complete_when_active(self) -> None:
        adapter, session = _make_adapter()
        adapter.start_task(_make_adapter_task())
        adapter.complete_task(uuid.uuid4())
        session.complete.assert_called_once()


class TestErrorBoundary:
    def test_session_error_becomes_adapter_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = RuntimeError("database locked")
        adapter, _ = _make_adapter(session=mock_session)
        task = _make_adapter_task()
        with pytest.raises(AdapterError, match="Internal error"):
            adapter.start_task(task)

    def test_learn_session_error_becomes_adapter_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.return_value = _make_context_package()
        mock_session.learn.side_effect = RuntimeError("storage failure")
        adapter, _ = _make_adapter(session=mock_session)
        adapter.start_task(_make_adapter_task())
        learning = _make_learning()
        with pytest.raises(AdapterError, match="Internal error"):
            adapter.learn(learning)

    def test_complete_session_error_becomes_adapter_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.return_value = _make_context_package()
        mock_session.complete.side_effect = RuntimeError("unexpected")
        adapter, _ = _make_adapter(session=mock_session)
        adapter.start_task(_make_adapter_task())
        with pytest.raises(AdapterError, match="Internal error"):
            adapter.complete_task(uuid.uuid4())


class TestDependencyInjection:
    def test_all_dependencies_injected(self) -> None:
        session = MagicMock()
        mapper = TaskMapper()
        lifecycle = AdapterLifecycle()
        adapter = BrainAdapter(session=session, mapper=mapper, lifecycle=lifecycle)
        assert adapter._session is session
        assert adapter._mapper is mapper
        assert adapter._lifecycle is lifecycle


class TestDeterministicBehavior:
    def test_same_input_same_output(self) -> None:
        adapter1, _ = _make_adapter()
        adapter2, _ = _make_adapter()
        task = _make_adapter_task()

        r1 = adapter1.start_task(task)
        r2 = adapter2.start_task(task)

        assert r1.task_id == r2.task_id
        assert r1.context.task == r2.context.task
