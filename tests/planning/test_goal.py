import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.task import Priority
from brain.planning.goal import Goal, GoalStatus


def make_goal(**kwargs) -> Goal:
    defaults = dict(
        title="Test Goal",
        description="A test goal description",
        project="test_project",
        priority=Priority.HIGH,
    )
    defaults.update(kwargs)
    return Goal(**defaults)


class TestGoalCreation:
    def test_create_valid(self):
        g = make_goal()
        assert isinstance(g.id, uuid.UUID)
        assert g.title == "Test Goal"
        assert g.description == "A test goal description"
        assert g.project == "test_project"
        assert g.priority == Priority.HIGH
        assert g.status == GoalStatus.ACTIVE
        assert isinstance(g.created_at, datetime)

    def test_custom_status(self):
        g = make_goal(status=GoalStatus.COMPLETED)
        assert g.status == GoalStatus.COMPLETED


class TestGoalImmutability:
    def test_frozen(self):
        g = make_goal()
        with pytest.raises(AttributeError):
            g.title = "changed"

    def test_status_frozen(self):
        g = make_goal()
        with pytest.raises(AttributeError):
            g.status = GoalStatus.BLOCKED


class TestGoalValidation:
    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="title must not be empty"):
            make_goal(title="")

    def test_whitespace_title_raises(self):
        with pytest.raises(ValueError, match="title must not be empty"):
            make_goal(title="  ")

    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_goal(description="")

    def test_empty_project_raises(self):
        with pytest.raises(ValueError, match="project must not be empty"):
            make_goal(project="")


class TestGoalStatus:
    def test_four_values(self):
        assert len(GoalStatus) == 4

    def test_values(self):
        assert GoalStatus.ACTIVE.value == "active"
        assert GoalStatus.COMPLETED.value == "completed"
        assert GoalStatus.BLOCKED.value == "blocked"
        assert GoalStatus.ABANDONED.value == "abandoned"
