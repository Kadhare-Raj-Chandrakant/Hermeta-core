import uuid
from unittest.mock import MagicMock

import pytest

from brain.adapter.errors import AdapterError, AdapterNotReadyError
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.task_mapper import TaskMapper
from brain.domain.enums import KnowledgeType
from brain.domain.task import TaskType
from brain.domain.version import KnowledgeVersion
from brain.integration.coordinator import IntegrationError, SessionCoordinator
from brain.integration.models import IntegrationLearning, IntegrationTask
from brain.services.compiler import ContextPackage
from brain.application.brain_session import BrainSession
from brain.domain.task import Priority


def _make_integration_task(task_type: str = "IMPLEMENT", **overrides) -> IntegrationTask:
    defaults = dict(
        task_id=uuid.uuid4(),
        objective="Implement login",
        project="atlas",
        component="auth",
        task_type=task_type,
    )
    defaults.update(overrides)
    return IntegrationTask(**defaults)


def _make_context_package() -> ContextPackage:
    from brain.domain.task import Task
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


def _make_coordinator(**overrides):
    session = overrides.pop("session", MagicMock())
    session.begin.return_value = _make_context_package()
    session.learn.return_value = _make_version()
    adapter = BrainAdapter(
        session=session,
        mapper=TaskMapper(),
        lifecycle=AdapterLifecycle(),
    )
    return SessionCoordinator(adapter=adapter), session


from brain.adapter.adapter import BrainAdapter


class TestStartTaskOrchestration:
    def test_transitions_to_ready_then_working(self) -> None:
        coordinator, _ = _make_coordinator()
        assert coordinator.state.value == "idle"
        task = _make_integration_task()
        coordinator.start_task(task)
        assert coordinator.state.value == "working"

    def test_returns_integration_context(self) -> None:
        coordinator, _ = _make_coordinator()
        task = _make_integration_task()
        result = coordinator.start_task(task)
        assert result.task_id == task.task_id

    def test_calls_adapter_with_correct_task(self) -> None:
        coordinator, session = _make_coordinator()
        task = _make_integration_task(task_type="DEBUG")
        coordinator.start_task(task)
        called_task = session.begin.call_args[0][0]
        assert called_task.task_type == TaskType.DEBUG


class TestLearnOrchestration:
    def test_learn_when_working(self) -> None:
        coordinator, session = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        learning = IntegrationLearning(
            task_id=uuid.uuid4(),
            knowledge_type="ARCHITECTURE",
            title="Auth Design",
            understanding="OAuth2",
            confidence=0.9,
        )
        coordinator.learn(learning)
        session.learn.assert_called_once()

    def test_learn_without_start_raises(self) -> None:
        coordinator, _ = _make_coordinator()
        learning = IntegrationLearning(
            task_id=uuid.uuid4(),
            knowledge_type="BUG",
            title="test",
            understanding="test",
            confidence=0.5,
        )
        with pytest.raises((IntegrationError, ValueError)):
            coordinator.learn(learning)


class TestCompleteTaskOrchestration:
    def test_complete_returns_to_idle(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        coordinator.complete_task(uuid.uuid4())
        assert coordinator.state.value == "idle"

    def test_complete_calls_adapter(self) -> None:
        coordinator, session = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        coordinator.complete_task(uuid.uuid4())
        session.complete.assert_called_once()


class TestErrorWrapping:
    def test_adapter_error_becomes_integration_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("storage locked")
        coordinator, _ = _make_coordinator(session=mock_session)
        task = _make_integration_task()
        with pytest.raises(IntegrationError):
            coordinator.start_task(task)

    def test_state_resets_on_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("fail")
        coordinator, _ = _make_coordinator(session=mock_session)
        try:
            coordinator.start_task(_make_integration_task())
        except IntegrationError:
            pass
        assert coordinator.state.value == "idle"


class TestDeterministicBehavior:
    def test_same_input_same_output(self) -> None:
        coordinator1, _ = _make_coordinator()
        coordinator2, _ = _make_coordinator()
        task = _make_integration_task()

        r1 = coordinator1.start_task(task)
        r2 = coordinator2.start_task(task)

        assert r1.task_id == r2.task_id
        assert len(r1.sections) == len(r2.sections)
