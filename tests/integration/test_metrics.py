import uuid
from unittest.mock import MagicMock

import pytest

from brain.adapter.adapter import BrainAdapter
from brain.adapter.errors import AdapterError
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.task_mapper import TaskMapper
from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.domain.version import KnowledgeVersion
from brain.integration.coordinator import IntegrationStatus, SessionCoordinator
from brain.integration.errors import IntegrationError
from brain.integration.facade import IntegrationLayer
from brain.integration.models import IntegrationLearning, IntegrationTask
from brain.services.compiler import ContextPackage


def _make_integration_task(**overrides) -> IntegrationTask:
    defaults = dict(
        task_id=uuid.uuid4(),
        objective="Implement login",
        project="atlas",
        component="auth",
        task_type="IMPLEMENT",
    )
    defaults.update(overrides)
    return IntegrationTask(**defaults)


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


def _make_layer(**overrides):
    session = overrides.pop("session", MagicMock())
    session.begin.return_value = _make_context_package()
    session.learn.return_value = _make_version()
    adapter = BrainAdapter(
        session=session,
        mapper=TaskMapper(),
        lifecycle=AdapterLifecycle(),
    )
    return IntegrationLayer(adapter=adapter), session


class TestIntegrationStatus:
    def test_initial_status(self) -> None:
        coordinator, _ = _make_coordinator()
        status = coordinator.status()
        assert isinstance(status, IntegrationStatus)
        assert status.state == "idle"
        assert status.tasks_started == 0
        assert status.tasks_completed == 0
        assert status.learn_operations == 0
        assert status.failures == 0

    def test_status_frozen(self) -> None:
        status = IntegrationStatus(
            state="idle",
            tasks_started=0,
            tasks_completed=0,
            learn_operations=0,
            failures=0,
        )
        with pytest.raises(AttributeError):
            status.state = "working"  # type: ignore[misc]


class TestCoordinatorMetrics:
    def test_tasks_started_counter(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        status = coordinator.status()
        assert status.tasks_started == 1

    def test_tasks_started_multiple(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        coordinator.complete_task(uuid.uuid4())
        coordinator.start_task(_make_integration_task())
        status = coordinator.status()
        assert status.tasks_started == 2

    def test_tasks_completed_counter(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        coordinator.complete_task(uuid.uuid4())
        status = coordinator.status()
        assert status.tasks_completed == 1

    def test_learn_operations_counter(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        learning = IntegrationLearning(
            task_id=uuid.uuid4(),
            knowledge_type="ARCHITECTURE",
            title="Auth Design",
            understanding="OAuth2",
            confidence=0.9,
        )
        coordinator.learn(learning)
        status = coordinator.status()
        assert status.learn_operations == 1

    def test_learn_operations_multiple(self) -> None:
        coordinator, _ = _make_coordinator()
        coordinator.start_task(_make_integration_task())
        for i in range(3):
            learning = IntegrationLearning(
                task_id=uuid.uuid4(),
                knowledge_type="ARCHITECTURE",
                title=f"Design {i}",
                understanding=f"Understanding {i}",
                confidence=0.9,
            )
            coordinator.learn(learning)
        status = coordinator.status()
        assert status.learn_operations == 3

    def test_failures_counter(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("fail")
        coordinator, _ = _make_coordinator(session=mock_session)
        try:
            coordinator.start_task(_make_integration_task())
        except IntegrationError:
            pass
        status = coordinator.status()
        assert status.failures == 1

    def test_failures_multiple(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("fail")
        coordinator, _ = _make_coordinator(session=mock_session)
        for _ in range(2):
            try:
                coordinator.start_task(_make_integration_task())
            except IntegrationError:
                pass
        status = coordinator.status()
        assert status.failures == 2


class TestFacadeMetrics:
    def test_status_delegates_to_coordinator(self) -> None:
        layer, _ = _make_layer()
        status = layer.status()
        assert status.state == "idle"
        assert status.tasks_started == 0

    def test_facade_metrics_count(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth",
            understanding="OAuth2",
            confidence=0.9,
        )
        layer.learn(learning)
        layer.complete_task(task.task_id)
        status = layer.status()
        assert status.tasks_started == 1
        assert status.tasks_completed == 1
        assert status.learn_operations == 1
        assert status.failures == 0
