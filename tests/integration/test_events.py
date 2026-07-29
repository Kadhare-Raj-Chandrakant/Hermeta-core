import uuid

import pytest

from brain.integration.events import (
    ContextPrepared,
    ContextUnavailable,
    KnowledgeLearned,
    LearningFailed,
    TaskCompleted,
    TaskStarted,
)


class TestTaskStarted:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = TaskStarted(task_id=task_id)
        assert event.task_id == task_id
        assert event.timestamp is not None

    def test_frozen(self) -> None:
        event = TaskStarted(task_id=uuid.uuid4())
        with pytest.raises(AttributeError):
            event.task_id = uuid.uuid4()  # type: ignore[misc]


class TestContextPrepared:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = ContextPrepared(task_id=task_id, section_count=3)
        assert event.task_id == task_id
        assert event.section_count == 3

    def test_frozen(self) -> None:
        event = ContextPrepared(task_id=uuid.uuid4(), section_count=1)
        with pytest.raises(AttributeError):
            event.section_count = 5  # type: ignore[misc]


class TestKnowledgeLearned:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = KnowledgeLearned(
            task_id=task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth Design",
        )
        assert event.task_id == task_id
        assert event.knowledge_type == "ARCHITECTURE"
        assert event.title == "Auth Design"

    def test_frozen(self) -> None:
        event = KnowledgeLearned(
            task_id=uuid.uuid4(),
            knowledge_type="BUG",
            title="test",
        )
        with pytest.raises(AttributeError):
            event.title = "new"  # type: ignore[misc]


class TestTaskCompleted:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = TaskCompleted(task_id=task_id)
        assert event.task_id == task_id

    def test_frozen(self) -> None:
        event = TaskCompleted(task_id=uuid.uuid4())
        with pytest.raises(AttributeError):
            event.task_id = uuid.uuid4()  # type: ignore[misc]


class TestLearningFailed:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = LearningFailed(task_id=task_id, reason="validation error")
        assert event.task_id == task_id
        assert event.reason == "validation error"

    def test_empty_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="reason must not be empty"):
            LearningFailed(task_id=uuid.uuid4(), reason="")

    def test_whitespace_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="reason must not be empty"):
            LearningFailed(task_id=uuid.uuid4(), reason="   ")

    def test_frozen(self) -> None:
        event = LearningFailed(task_id=uuid.uuid4(), reason="test")
        with pytest.raises(AttributeError):
            event.reason = "new"  # type: ignore[misc]


class TestContextUnavailable:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        event = ContextUnavailable(task_id=task_id, reason="adapter error")
        assert event.task_id == task_id
        assert event.reason == "adapter error"

    def test_empty_reason_raises(self) -> None:
        with pytest.raises(ValueError, match="reason must not be empty"):
            ContextUnavailable(task_id=uuid.uuid4(), reason="")

    def test_frozen(self) -> None:
        event = ContextUnavailable(task_id=uuid.uuid4(), reason="test")
        with pytest.raises(AttributeError):
            event.reason = "new"  # type: ignore[misc]
