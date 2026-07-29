import uuid

import pytest

from brain.domain.task import Task, TaskType, Priority
from brain.retrieval.conditions.task_type import TaskTypeCondition
from brain.retrieval.trigger import RetrievalTrigger


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


class TestRetrievalTrigger:
    def test_creation(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger = RetrievalTrigger(
            name="test trigger",
            description="A test trigger",
            condition=condition,
            priority=5,
        )
        assert trigger.name == "test trigger"
        assert trigger.description == "A test trigger"
        assert trigger.condition is condition
        assert trigger.priority == 5
        assert trigger.enabled is True
        assert isinstance(trigger.id, uuid.UUID)
        assert trigger.created_at is not None

    def test_immutability(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger = RetrievalTrigger(
            name="test",
            description="desc",
            condition=condition,
        )
        with pytest.raises(AttributeError):
            trigger.name = "new"  # type: ignore[misc]

    def test_default_enabled(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger = RetrievalTrigger(
            name="test",
            description="desc",
            condition=condition,
        )
        assert trigger.enabled is True

    def test_default_priority(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger = RetrievalTrigger(
            name="test",
            description="desc",
            condition=condition,
        )
        assert trigger.priority == 0

    def test_empty_name_raises(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        with pytest.raises(ValueError, match="name must not be empty"):
            RetrievalTrigger(
                name="",
                description="desc",
                condition=condition,
            )

    def test_whitespace_name_raises(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        with pytest.raises(ValueError, match="name must not be empty"):
            RetrievalTrigger(
                name="   ",
                description="desc",
                condition=condition,
            )

    def test_empty_description_raises(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        with pytest.raises(ValueError, match="description must not be empty"):
            RetrievalTrigger(
                name="test",
                description="",
                condition=condition,
            )

    def test_whitespace_description_raises(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        with pytest.raises(ValueError, match="description must not be empty"):
            RetrievalTrigger(
                name="test",
                description="   ",
                condition=condition,
            )

    def test_negative_priority_raises(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        with pytest.raises(ValueError, match="priority must be >= 0"):
            RetrievalTrigger(
                name="test",
                description="desc",
                condition=condition,
                priority=-1,
            )

    def test_priority_zero_valid(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger = RetrievalTrigger(
            name="test",
            description="desc",
            condition=condition,
            priority=0,
        )
        assert trigger.priority == 0

    def test_equality_by_id(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        trigger1 = RetrievalTrigger(
            name="same",
            description="same",
            condition=condition,
        )
        trigger2 = RetrievalTrigger(
            name="same",
            description="same",
            condition=condition,
        )
        assert trigger1.id != trigger2.id
        assert trigger1 != trigger2
