import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.retrieval.conditions.component import ComponentCondition
from brain.retrieval.conditions.keyword import KeywordCondition
from brain.retrieval.conditions.knowledge_type import KnowledgeTypeCondition
from brain.retrieval.conditions.project import ProjectCondition
from brain.retrieval.conditions.task_type import TaskTypeCondition
from brain.retrieval.engine import RetrievalTriggerEngine
from brain.retrieval.trigger import RetrievalTrigger


def _make_task(**overrides) -> Task:
    defaults = dict(
        task_type=TaskType.IMPLEMENT,
        project="atlas",
        component="auth",
        objective="Implement login flow",
        constraints=(),
        priority=Priority.MEDIUM,
    )
    defaults.update(overrides)
    return Task(**defaults)


def _make_trigger(
    name: str = "test",
    condition=None,
    priority: int = 0,
    enabled: bool = True,
) -> RetrievalTrigger:
    if condition is None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
    return RetrievalTrigger(
        name=name,
        description=f"Trigger: {name}",
        condition=condition,
        priority=priority,
        enabled=enabled,
    )


class TestRetrievalTriggerEngine:
    def test_empty_triggers(self) -> None:
        engine = RetrievalTriggerEngine(())
        task = _make_task()
        result = engine.evaluate(task)
        assert result == ()

    def test_no_matching_triggers(self) -> None:
        trigger = _make_trigger(
            condition=TaskTypeCondition((TaskType.DEBUG,))
        )
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task(task_type=TaskType.IMPLEMENT)
        result = engine.evaluate(task)
        assert result == ()

    def test_single_matching_trigger(self) -> None:
        trigger = _make_trigger(
            condition=TaskTypeCondition((TaskType.IMPLEMENT,))
        )
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        assert request.task is task
        assert trigger.id in request.trigger_ids

    def test_disabled_trigger_ignored(self) -> None:
        trigger = _make_trigger(enabled=False)
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task()
        result = engine.evaluate(task)
        assert result == ()

    def test_multiple_triggers(self) -> None:
        t1 = _make_trigger(
            name="task type",
            condition=TaskTypeCondition((TaskType.IMPLEMENT,)),
            priority=1,
        )
        t2 = _make_trigger(
            name="project",
            condition=ProjectCondition(("atlas",)),
            priority=2,
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        assert t1.id in request.trigger_ids
        assert t2.id in request.trigger_ids

    def test_priority_ordering(self) -> None:
        t1 = _make_trigger(
            name="low priority",
            condition=TaskTypeCondition((TaskType.IMPLEMENT,)),
            priority=1,
        )
        t2 = _make_trigger(
            name="high priority",
            condition=ProjectCondition(("atlas",)),
            priority=10,
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        assert request.trigger_ids[0] == t2.id
        assert request.trigger_ids[1] == t1.id

    def test_knowledge_types_combined(self) -> None:
        t1 = _make_trigger(
            name="architecture",
            condition=KnowledgeTypeCondition((KnowledgeType.ARCHITECTURE,)),
        )
        t2 = _make_trigger(
            name="decision",
            condition=KnowledgeTypeCondition((KnowledgeType.DECISION,)),
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        kt_set = set(request.knowledge_types)
        assert KnowledgeType.ARCHITECTURE in kt_set
        assert KnowledgeType.DECISION in kt_set

    def test_duplicate_knowledge_types_removed(self) -> None:
        t1 = _make_trigger(
            name="arch1",
            condition=KnowledgeTypeCondition((KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION)),
        )
        t2 = _make_trigger(
            name="arch2",
            condition=KnowledgeTypeCondition((KnowledgeType.ARCHITECTURE,)),
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        assert len(request.knowledge_types) == 2
        assert KnowledgeType.ARCHITECTURE in request.knowledge_types
        assert KnowledgeType.DECISION in request.knowledge_types

    def test_reason_combined(self) -> None:
        t1 = _make_trigger(
            name="t1",
            condition=TaskTypeCondition((TaskType.IMPLEMENT,)),
        )
        t2 = _make_trigger(
            name="t2",
            condition=ProjectCondition(("atlas",)),
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        request = result[0]
        assert "Trigger: t1" in request.reason
        assert "Trigger: t2" in request.reason

    def test_deterministic_output(self) -> None:
        trigger = _make_trigger(
            condition=TaskTypeCondition((TaskType.IMPLEMENT,))
        )
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task()
        r1 = engine.evaluate(task)
        r2 = engine.evaluate(task)
        assert r1[0].knowledge_types == r2[0].knowledge_types
        assert r1[0].trigger_ids == r2[0].trigger_ids
        assert r1[0].reason == r2[0].reason

    def test_mixed_conditions_all_match(self) -> None:
        t1 = _make_trigger(
            name="task type",
            condition=TaskTypeCondition((TaskType.IMPLEMENT,)),
            priority=3,
        )
        t2 = _make_trigger(
            name="project",
            condition=ProjectCondition(("atlas",)),
            priority=2,
        )
        t3 = _make_trigger(
            name="component",
            condition=ComponentCondition(("auth",)),
            priority=1,
        )
        engine = RetrievalTriggerEngine((t1, t2, t3))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        assert len(result[0].trigger_ids) == 3

    def test_partial_condition_match(self) -> None:
        t1 = _make_trigger(
            name="task type",
            condition=TaskTypeCondition((TaskType.IMPLEMENT,)),
        )
        t2 = _make_trigger(
            name="project",
            condition=ProjectCondition(("other_project",)),
        )
        engine = RetrievalTriggerEngine((t1, t2))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        assert result[0].trigger_ids == (t1.id,)

    def test_keyword_matching(self) -> None:
        trigger = _make_trigger(
            name="keyword",
            condition=KeywordCondition(("login",)),
        )
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task(objective="Fix login bug")
        result = engine.evaluate(task)
        assert len(result) == 1

    def test_no_knowledge_types_from_non_kt_conditions(self) -> None:
        trigger = _make_trigger(
            condition=TaskTypeCondition((TaskType.IMPLEMENT,))
        )
        engine = RetrievalTriggerEngine((trigger,))
        task = _make_task()
        result = engine.evaluate(task)
        assert len(result) == 1
        assert result[0].knowledge_types == ()
