import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.retrieval.request import RetrievalRequest


def _make_task(**overrides) -> Task:
    defaults = dict(
        task_type=TaskType.IMPLEMENT,
        project="atlas",
        component="auth",
        objective="Implement login",
        constraints=(),
        priority=Priority.MEDIUM,
    )
    defaults.update(overrides)
    return Task(**defaults)


class TestRetrievalRequest:
    def test_creation(self) -> None:
        task = _make_task()
        request = RetrievalRequest(
            task=task,
            trigger_ids=(uuid.uuid4(),),
            knowledge_types=(KnowledgeType.ARCHITECTURE,),
            reason="Load architecture knowledge",
        )
        assert request.task is task
        assert len(request.trigger_ids) == 1
        assert request.knowledge_types == (KnowledgeType.ARCHITECTURE,)
        assert request.reason == "Load architecture knowledge"
        assert isinstance(request.id, uuid.UUID)
        assert request.created_at is not None

    def test_immutability(self) -> None:
        task = _make_task()
        request = RetrievalRequest(
            task=task,
            trigger_ids=(),
            knowledge_types=(),
            reason="test reason",
        )
        with pytest.raises(AttributeError):
            request.reason = "new"  # type: ignore[misc]

    def test_empty_reason_raises(self) -> None:
        task = _make_task()
        with pytest.raises(ValueError, match="reason must not be empty"):
            RetrievalRequest(
                task=task,
                trigger_ids=(),
                knowledge_types=(),
                reason="",
            )

    def test_whitespace_reason_raises(self) -> None:
        task = _make_task()
        with pytest.raises(ValueError, match="reason must not be empty"):
            RetrievalRequest(
                task=task,
                trigger_ids=(),
                knowledge_types=(),
                reason="   ",
            )

    def test_empty_trigger_ids(self) -> None:
        task = _make_task()
        request = RetrievalRequest(
            task=task,
            trigger_ids=(),
            knowledge_types=(),
            reason="test",
        )
        assert request.trigger_ids == ()

    def test_empty_knowledge_types(self) -> None:
        task = _make_task()
        request = RetrievalRequest(
            task=task,
            trigger_ids=(),
            knowledge_types=(),
            reason="test",
        )
        assert request.knowledge_types == ()

    def test_equality_by_id(self) -> None:
        task = _make_task()
        r1 = RetrievalRequest(
            task=task,
            trigger_ids=(),
            knowledge_types=(),
            reason="same",
        )
        r2 = RetrievalRequest(
            task=task,
            trigger_ids=(),
            knowledge_types=(),
            reason="same",
        )
        assert r1.id != r2.id
        assert r1 != r2
