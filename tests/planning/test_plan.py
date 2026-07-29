import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.task import Priority
from brain.planning.action import Action
from brain.planning.blocker import Blocker, BlockerSeverity
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal
from brain.planning.plan import Plan, PlanStatus


def make_goal(**kwargs) -> Goal:
    defaults = dict(
        title="Test Goal",
        description="Test description",
        project="test_project",
        priority=Priority.HIGH,
    )
    defaults.update(kwargs)
    return Goal(**defaults)


def make_plan(**kwargs) -> Plan:
    defaults = dict(
        goal=make_goal(),
        actions=(),
        dependencies=(),
        blockers=(),
        confidence=0.8,
    )
    defaults.update(kwargs)
    return Plan(**defaults)


class TestPlanCreation:
    def test_create_valid(self):
        p = make_plan()
        assert isinstance(p.id, uuid.UUID)
        assert isinstance(p.goal, Goal)
        assert p.actions == ()
        assert p.dependencies == ()
        assert p.blockers == ()
        assert p.confidence == 0.8
        assert p.status == PlanStatus.DRAFT
        assert isinstance(p.created_at, datetime)

    def test_with_actions(self):
        action = Action(
            goal_id=uuid.uuid4(),
            title="Do something",
            description="Description",
        )
        p = make_plan(actions=(action,))
        assert len(p.actions) == 1


class TestPlanImmutability:
    def test_frozen(self):
        p = make_plan()
        with pytest.raises(AttributeError):
            p.confidence = 0.5

    def test_actions_frozen(self):
        p = make_plan()
        with pytest.raises(AttributeError):
            p.actions = ()

    def test_status_frozen(self):
        p = make_plan()
        with pytest.raises(AttributeError):
            p.status = PlanStatus.ACTIVE


class TestPlanValidation:
    def test_negative_confidence_raises(self):
        with pytest.raises(ValueError, match="confidence must be between"):
            make_plan(confidence=-0.1)

    def test_confidence_above_one_raises(self):
        with pytest.raises(ValueError, match="confidence must be between"):
            make_plan(confidence=1.1)

    def test_zero_confidence_valid(self):
        p = make_plan(confidence=0.0)
        assert p.confidence == 0.0

    def test_one_confidence_valid(self):
        p = make_plan(confidence=1.0)
        assert p.confidence == 1.0


class TestPlanStatus:
    def test_five_values(self):
        assert len(PlanStatus) == 5

    def test_values(self):
        assert PlanStatus.DRAFT.value == "draft"
        assert PlanStatus.ACTIVE.value == "active"
        assert PlanStatus.COMPLETED.value == "completed"
        assert PlanStatus.FAILED.value == "failed"
        assert PlanStatus.ABANDONED.value == "abandoned"
