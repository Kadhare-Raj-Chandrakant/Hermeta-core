import uuid
from unittest.mock import MagicMock

import pytest

from brain.adapter.adapter import BrainAdapter
from brain.adapter.errors import AdapterError
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.task_mapper import TaskMapper
from brain.domain.enums import KnowledgeType
from brain.domain.version import KnowledgeVersion
from brain.integration.coordinator import IntegrationError
from brain.integration.events import (
    ContextPrepared,
    ContextUnavailable,
    KnowledgeLearned,
    LearningFailed,
    TaskCompleted,
    TaskStarted,
)
from brain.integration.integration import EventRecorder, IntegrationLayer
from brain.integration.models import IntegrationLearning, IntegrationTask
from brain.services.compiler import ContextPackage
from brain.application.brain_session import BrainSession
from brain.domain.task import Task, TaskType, Priority


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


class TestEventRecorder:
    def test_empty_events(self) -> None:
        recorder = EventRecorder()
        assert recorder.events == ()

    def test_record_event(self) -> None:
        recorder = EventRecorder()
        event = TaskStarted(task_id=uuid.uuid4())
        recorder.record(event)
        assert len(recorder.events) == 1
        assert recorder.events[0] is event

    def test_record_multiple(self) -> None:
        recorder = EventRecorder()
        e1 = TaskStarted(task_id=uuid.uuid4())
        e2 = TaskCompleted(task_id=uuid.uuid4())
        recorder.record(e1)
        recorder.record(e2)
        assert len(recorder.events) == 2

    def test_events_returns_tuple(self) -> None:
        recorder = EventRecorder()
        recorder.record(TaskStarted(task_id=uuid.uuid4()))
        result = recorder.events
        assert isinstance(result, tuple)

    def test_events_immutable(self) -> None:
        recorder = EventRecorder()
        recorder.record(TaskStarted(task_id=uuid.uuid4()))
        events = recorder.events
        with pytest.raises(TypeError):
            events[0] = None  # type: ignore[assignment]


class TestIntegrationLayerStartTask:
    def test_records_task_started(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        assert isinstance(layer.events[0], TaskStarted)
        assert layer.events[0].task_id == task.task_id

    def test_records_context_prepared(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        assert isinstance(layer.events[1], ContextPrepared)
        assert layer.events[1].task_id == task.task_id

    def test_returns_integration_context(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        result = layer.start_task(task)
        assert result.task_id == task.task_id

    def test_state_transitions(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        assert layer.state.value == "working"


class TestIntegrationLayerLearn:
    def test_records_knowledge_learned(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth Design",
            understanding="OAuth2",
            confidence=0.9,
        )
        layer.learn(learning)
        assert any(isinstance(e, KnowledgeLearned) for e in layer.events)

    def test_records_learning_failed_on_error(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.return_value = _make_context_package()
        mock_session.learn.side_effect = AdapterError("storage fail")
        layer, _ = _make_layer(session=mock_session)
        task = _make_integration_task()
        layer.start_task(task)
        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="BUG",
            title="test",
            understanding="test",
            confidence=0.5,
        )
        with pytest.raises(IntegrationError):
            layer.learn(learning)
        assert any(isinstance(e, LearningFailed) for e in layer.events)


class TestIntegrationLayerComplete:
    def test_records_task_completed(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        layer.complete_task(task.task_id)
        assert any(isinstance(e, TaskCompleted) for e in layer.events)

    def test_state_returns_to_idle(self) -> None:
        layer, _ = _make_layer()
        task = _make_integration_task()
        layer.start_task(task)
        layer.complete_task(task.task_id)
        assert layer.state.value == "idle"


class TestIntegrationLayerErrorBoundary:
    def test_adapter_error_wrapped(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("locked")
        layer, _ = _make_layer(session=mock_session)
        with pytest.raises(IntegrationError):
            layer.start_task(_make_integration_task())

    def test_context_unavailable_recorded(self) -> None:
        mock_session = MagicMock()
        mock_session.begin.side_effect = AdapterError("locked")
        layer, _ = _make_layer(session=mock_session)
        try:
            layer.start_task(_make_integration_task())
        except IntegrationError:
            pass
        assert any(isinstance(e, ContextUnavailable) for e in layer.events)


class TestDeterministicBehavior:
    def test_same_input_same_output(self) -> None:
        layer1, _ = _make_layer()
        layer2, _ = _make_layer()
        task = _make_integration_task()

        r1 = layer1.start_task(task)
        r2 = layer2.start_task(task)

        assert r1.task_id == r2.task_id
        assert len(r1.sections) == len(r2.sections)

    def test_same_input_same_events(self) -> None:
        layer1, _ = _make_layer()
        layer2, _ = _make_layer()
        task = _make_integration_task()

        layer1.start_task(task)
        layer2.start_task(task)

        assert len(layer1.events) == len(layer2.events)
        assert type(layer1.events[0]) is type(layer2.events[0])
