from unittest.mock import MagicMock

import pytest

from brain.application.brain_service import BrainService
from brain.application.brain_session import BrainSession, SessionStatus
from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence as DomainEvidence
from brain.pipeline.evidence import Evidence
from brain.domain.task import Task, TaskType, Priority
from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate
from brain.services.compiler import ContextPackage, ContextSection


def make_task() -> Task:
    return Task(
        task_type=TaskType.IMPLEMENT,
        project="hermes-brain",
        component="brain-session",
        objective="implement session orchestration",
        constraints=(),
        priority=Priority.HIGH,
    )


def make_candidate() -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=KnowledgeType.DECISION,
        title="Test decision",
        understanding="Test understanding",
        confidence=0.8,
        evidence_source=Evidence(source_type="conversation", content="test"),
    )


def make_version() -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=__import__("uuid").uuid4(),
        version_number=1,
        knowledge_type=KnowledgeType.DECISION,
        title="Test version",
        understanding="Test understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(DomainEvidence(source="conversation", reference="test"),),
        relationships=(),
        created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )


class TestSessionBegin:
    def test_begin_returns_context_package(self):
        mock_brain = MagicMock(spec=BrainService)
        expected = MagicMock(spec=ContextPackage)
        mock_brain.prepare.return_value = expected

        session = BrainSession(mock_brain)
        task = make_task()
        result = session.begin(task)

        assert result is expected
        mock_brain.prepare.assert_called_once_with(task)

    def test_begin_sets_active(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)

        session = BrainSession(mock_brain)
        session.begin(make_task())

        status = session.status()
        assert status.active is True

    def test_begin_records_task(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)

        session = BrainSession(mock_brain)
        task = make_task()
        session.begin(task)

        status = session.status()
        assert status.task is task

    def test_begin_records_timestamp(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)

        session = BrainSession(mock_brain)
        session.begin(make_task())

        status = session.status()
        assert status.started_at is not None

    def test_begin_fails_when_already_active(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)

        session = BrainSession(mock_brain)
        session.begin(make_task())

        with pytest.raises(RuntimeError, match="already active"):
            session.begin(make_task())


class TestSessionLearn:
    def test_learn_returns_knowledge_version(self):
        mock_brain = MagicMock(spec=BrainService)
        expected = make_version()
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = expected

        session = BrainSession(mock_brain)
        session.begin(make_task())
        result = session.learn(make_candidate())

        assert result is expected

    def test_learn_calls_brain_service(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        candidate = make_candidate()
        session.learn(candidate)

        mock_brain.learn.assert_called_once_with(candidate)

    def test_learn_increments_count(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.learn(make_candidate())
        session.learn(make_candidate())

        status = session.status()
        assert status.learned_items == 2

    def test_learn_fails_when_no_session(self):
        mock_brain = MagicMock(spec=BrainService)

        session = BrainSession(mock_brain)
        with pytest.raises(RuntimeError, match="No active session"):
            session.learn(make_candidate())


class TestSessionComplete:
    def test_complete_clears_state(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.learn(make_candidate())
        session.complete()

        status = session.status()
        assert status.active is False
        assert status.started_at is None
        assert status.task is None
        assert status.learned_items == 0

    def test_complete_fails_when_no_session(self):
        mock_brain = MagicMock(spec=BrainService)

        session = BrainSession(mock_brain)
        with pytest.raises(RuntimeError, match="No active session"):
            session.complete()

    def test_can_begin_new_session_after_complete(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.complete()

        session.begin(make_task())
        session.learn(make_candidate())

        status = session.status()
        assert status.active is True
        assert status.learned_items == 1


class TestMultipleLearnCalls:
    def test_multiple_learn_calls(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())

        versions = []
        for _ in range(5):
            versions.append(session.learn(make_candidate()))

        assert len(versions) == 5
        assert session.status().learned_items == 5
        assert mock_brain.learn.call_count == 5


class TestDeterministicBehavior:
    def test_same_input_same_output(self):
        mock_brain = MagicMock(spec=BrainService)
        expected = make_version()
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = expected

        session1 = BrainSession(mock_brain)
        session1.begin(make_task())
        result1 = session1.learn(make_candidate())

        session2 = BrainSession(mock_brain)
        session2.begin(make_task())
        result2 = session2.learn(make_candidate())

        assert result1 is expected
        assert result2 is expected


class TestDependencyInjection:
    def test_session_uses_injected_brain(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.learn(make_candidate())

        mock_brain.prepare.assert_called_once()
        mock_brain.learn.assert_called_once()

    def test_status_returns_immutable(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)

        session = BrainSession(mock_brain)
        session.begin(make_task())

        status = session.status()
        assert isinstance(status, SessionStatus)


class TestOrchestrationOrder:
    def test_prepare_called_before_learn(self):
        call_order = []
        mock_brain = MagicMock(spec=BrainService)

        def track_prepare(task):
            call_order.append("prepare")
            return MagicMock(spec=ContextPackage)

        def track_learn(candidate):
            call_order.append("learn")
            return make_version()

        mock_brain.prepare.side_effect = track_prepare
        mock_brain.learn.side_effect = track_learn

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.learn(make_candidate())

        assert call_order == ["prepare", "learn"]

    def test_no_duplicated_brain_service_calls(self):
        mock_brain = MagicMock(spec=BrainService)
        mock_brain.prepare.return_value = MagicMock(spec=ContextPackage)
        mock_brain.learn.return_value = make_version()

        session = BrainSession(mock_brain)
        session.begin(make_task())
        session.learn(make_candidate())
        session.learn(make_candidate())

        assert mock_brain.prepare.call_count == 1
        assert mock_brain.learn.call_count == 2


class TestInitialStatus:
    def test_fresh_session_not_active(self):
        mock_brain = MagicMock(spec=BrainService)
        session = BrainSession(mock_brain)

        status = session.status()
        assert status.active is False
        assert status.started_at is None
        assert status.task is None
        assert status.learned_items == 0
