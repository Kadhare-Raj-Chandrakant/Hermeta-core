import pytest

from brain.events.types import (
    ConflictDetected,
    ExecutionCompleted,
    ExecutionFailed,
    KnowledgeLearned,
    PlanCompleted,
    ReflectionCompleted,
)
from brain.events.event import Event


class TestKnowledgeLearned:
    def test_create(self):
        e = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        assert e.knowledge_type == "DECISION"
        assert e.title == "Test"
        assert isinstance(e, Event)

    def test_frozen(self):
        e = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        with pytest.raises(AttributeError):
            e.title = "Changed"

    def test_defaults(self):
        e = KnowledgeLearned()
        assert e.knowledge_type == ""
        assert e.title == ""


class TestExecutionCompleted:
    def test_create(self):
        e = ExecutionCompleted(plan_id="plan-1", actions_completed=5)
        assert e.plan_id == "plan-1"
        assert e.actions_completed == 5
        assert isinstance(e, Event)

    def test_frozen(self):
        e = ExecutionCompleted(plan_id="plan-1", actions_completed=5)
        with pytest.raises(AttributeError):
            e.plan_id = "changed"


class TestExecutionFailed:
    def test_create(self):
        e = ExecutionFailed(plan_id="plan-1", error="timeout")
        assert e.plan_id == "plan-1"
        assert e.error == "timeout"
        assert isinstance(e, Event)

    def test_frozen(self):
        e = ExecutionFailed(plan_id="plan-1", error="timeout")
        with pytest.raises(AttributeError):
            e.error = "changed"


class TestReflectionCompleted:
    def test_create(self):
        e = ReflectionCompleted(findings_count=3)
        assert e.findings_count == 3
        assert isinstance(e, Event)


class TestConflictDetected:
    def test_create(self):
        e = ConflictDetected(description="conflicting knowledge")
        assert e.description == "conflicting knowledge"
        assert isinstance(e, Event)


class TestPlanCompleted:
    def test_create(self):
        e = PlanCompleted(plan_id="plan-1", confidence=0.85)
        assert e.plan_id == "plan-1"
        assert e.confidence == 0.85
        assert isinstance(e, Event)
