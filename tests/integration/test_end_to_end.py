import uuid

import pytest

from brain.adapter.adapter import BrainAdapter
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.task_mapper import TaskMapper
from brain.application.brain_service import BrainService
from brain.domain.enums import KnowledgeType
from brain.domain.task import TaskType
from brain.domain.version import KnowledgeVersion
from brain.integration.errors import IntegrationError
from brain.integration.events import (
    ContextPrepared,
    ContextUnavailable,
    KnowledgeLearned,
    LearningFailed,
    TaskCompleted,
    TaskStarted,
)
from brain.integration.facade import IntegrationLayer
from brain.integration.models import IntegrationLearning, IntegrationTask
from brain.application.brain_session import BrainSession
from brain.pipeline.version_creator import VersionCreator
from brain.repositories.memory import InMemoryKnowledgeRepository
from brain.services.selection import SelectionEngine
from brain.services.compiler import ContextCompiler
from brain.services.relevance import RelevanceEngine
from brain.validation.engine import ValidationEngine
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.rules.type_rules import TypeRules


def _make_full_stack():
    repo = InMemoryKnowledgeRepository()
    relevance = RelevanceEngine()
    selection = SelectionEngine()
    compiler = ContextCompiler()
    validation_engine = ValidationEngine(rules=[ConfidenceRule(), CompletenessRule(), EvidenceRule(), TypeRules()])
    version_creator = VersionCreator()
    brain = BrainService(
        repository=repo,
        validator=validation_engine,
        version_creator=version_creator,
        relevance_engine=relevance,
        selection_engine=selection,
        context_compiler=compiler,
    )
    session = BrainSession(brain=brain)
    adapter = BrainAdapter(
        session=session,
        mapper=TaskMapper(),
        lifecycle=AdapterLifecycle(),
    )
    return IntegrationLayer(adapter=adapter), repo


class TestEndToEndFlow:
    def test_hermes_to_service_full_cycle(self) -> None:
        layer, repo = _make_full_stack()
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Implement OAuth2 login",
            project="atlas",
            component="auth",
            task_type="IMPLEMENT",
        )

        context = layer.start_task(task)
        assert context.task_id == task.task_id
        assert layer.state.value == "working"

        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth Architecture",
            understanding="OAuth2 with PKCE flow",
            confidence=0.9,
        )
        layer.learn(learning)

        versions = repo.list_all_versions()
        assert len(versions) == 1
        assert versions[0].title == "Auth Architecture"
        assert versions[0].knowledge_type == KnowledgeType.ARCHITECTURE

        layer.complete_task(task.task_id)
        assert layer.state.value == "idle"

    def test_multiple_knowledge_in_session(self) -> None:
        layer, repo = _make_full_stack()
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Refactor database layer",
            project="atlas",
            component="db",
            task_type="REFACTOR",
        )
        layer.start_task(task)

        learnings = [
            IntegrationLearning(
                task_id=task.task_id,
                knowledge_type="ARCHITECTURE",
                title="DB Pattern",
                understanding="Repository pattern",
                confidence=0.8,
            ),
            IntegrationLearning(
                task_id=task.task_id,
                knowledge_type="DECISION",
                title="DB Choice",
                understanding="The rationale for SQLite trades simplicity for scalability in the MVP",
                confidence=0.95,
            ),
        ]
        for learning in learnings:
            layer.learn(learning)

        versions = repo.list_all_versions()
        assert len(versions) == 2

        layer.complete_task(task.task_id)
        assert layer.state.value == "idle"

    def test_full_cycle_events_recorded(self) -> None:
        layer, _ = _make_full_stack()
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Fix auth bug",
            project="atlas",
            component="auth",
            task_type="DEBUG",
        )
        layer.start_task(task)
        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="BUG",
            title="Auth component timeout",
            understanding="Token expires too early in auth component",
            confidence=0.7,
        )
        layer.learn(learning)
        layer.complete_task(task.task_id)

        events = layer.events
        assert isinstance(events[0], TaskStarted)
        assert isinstance(events[1], ContextPrepared)
        assert isinstance(events[2], KnowledgeLearned)
        assert isinstance(events[3], TaskCompleted)
        assert len(events) == 4

    def test_error_does_not_leak_brain_internals(self) -> None:
        layer, _ = _make_full_stack()

        bad_task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Test",
            project="atlas",
            component="auth",
            task_type="INVALID_TYPE",
        )
        with pytest.raises(IntegrationError):
            layer.start_task(bad_task)

    def test_no_layer_bypass(self) -> None:
        layer, _ = _make_full_stack()
        coordinator = layer._coordinator
        assert hasattr(coordinator, "_adapter")
        adapter = coordinator._adapter
        assert isinstance(adapter, BrainAdapter)
        assert hasattr(adapter, "_session")
        session = adapter._session
        assert isinstance(session, BrainSession)

    def test_coordinator_state_lifecycle(self) -> None:
        layer, _ = _make_full_stack()
        assert layer.state.value == "idle"

        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Test",
            project="atlas",
            component="auth",
            task_type="IMPLEMENT",
        )
        layer.start_task(task)
        assert layer.state.value == "working"

        layer.complete_task(task.task_id)
        assert layer.state.value == "idle"

    def test_adapter_boundary_only_entry(self) -> None:
        layer, _ = _make_full_stack()
        coordinator = layer._coordinator
        adapter = coordinator._adapter
        assert hasattr(adapter, "start_task")
        assert hasattr(adapter, "learn")
        assert hasattr(adapter, "complete_task")

    def test_deterministic_output(self) -> None:
        layer1, _ = _make_full_stack()
        layer2, _ = _make_full_stack()
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Test determinism",
            project="atlas",
            component="auth",
            task_type="IMPLEMENT",
        )

        ctx1 = layer1.start_task(task)
        ctx2 = layer2.start_task(task)
        assert ctx1.task_id == ctx2.task_id

    def test_status_through_full_cycle(self) -> None:
        layer, _ = _make_full_stack()
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Test status",
            project="atlas",
            component="auth",
            task_type="IMPLEMENT",
        )
        layer.start_task(task)
        learning = IntegrationLearning(
            task_id=task.task_id,
            knowledge_type="ARCHITECTURE",
            title="Status Test",
            understanding="test",
            confidence=0.5,
        )
        layer.learn(learning)
        layer.complete_task(task.task_id)

        status = layer.status()
        assert status.tasks_started == 1
        assert status.tasks_completed == 1
        assert status.learn_operations == 1
        assert status.failures == 0
