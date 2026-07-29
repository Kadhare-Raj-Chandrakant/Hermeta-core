import uuid

import pytest

from brain.runtime import create_memory_runtime, create_sqlite_runtime, BrainRuntime, check_health
from brain.adapter.errors import AdapterError
from brain.adapter.models import AdapterLearning, AdapterTask
from brain.domain.task import TaskType


def _make_task() -> AdapterTask:
    return AdapterTask(
        task_id=uuid.uuid4(),
        task_type=TaskType.IMPLEMENT,
        objective="Implement feature",
        project="test",
        component="core",
        metadata={},
    )


class TestMemoryRuntimeLifecycle:
    def test_start_task_returns_context(self):
        r = create_memory_runtime()
        task = _make_task()
        ctx = r.adapter.start_task(task)
        assert ctx.task_id == task.task_id
        assert ctx.context is not None

    def test_learn_and_retrieve(self):
        r = create_memory_runtime()
        task = _make_task()
        r.adapter.start_task(task)
        learning = AdapterLearning(
            task_id=task.task_id,
            knowledge_type="ARCHITECTURE",
            title="System Architecture Overview",
            understanding="The system uses a layered architecture with domain-driven design principles and clean separation of concerns",
            confidence=0.9,
        )
        r.adapter.learn(learning)
        r.adapter.complete_task(task.task_id)
        versions = r.repository.list_all_versions()
        assert len(versions) == 1
        assert versions[0].title == "System Architecture Overview"

    def test_complete_task(self):
        r = create_memory_runtime()
        task = _make_task()
        r.adapter.start_task(task)
        learning = AdapterLearning(
            task_id=task.task_id,
            knowledge_type="RULE",
            title="Code Style Rule",
            understanding="Always use type hints in Python code to improve readability and maintainability",
            confidence=0.95,
        )
        r.adapter.learn(learning)
        r.adapter.complete_task(task.task_id)
        status = r.session.status()
        assert not status.active

    def test_multiple_knowledge_items(self):
        r = create_memory_runtime()
        task = _make_task()
        r.adapter.start_task(task)
        for i in range(3):
            learning = AdapterLearning(
                task_id=task.task_id,
                knowledge_type="PATTERN",
                title=f"Pattern {i}",
                understanding=f"This pattern describes approach number {i} for solving problems efficiently",
                confidence=0.7 + i * 0.1,
            )
            r.adapter.learn(learning)
        r.adapter.complete_task(task.task_id)
        versions = r.repository.list_all_versions()
        assert len(versions) == 3


class TestSQLiteRuntimePersistence:
    def test_knowledge_survives(self):
        import gc
        import tempfile
        import os

        path = tempfile.mktemp(suffix=".db")
        try:
            r1 = create_sqlite_runtime(path)
            task = _make_task()
            r1.adapter.start_task(task)
            learning = AdapterLearning(
                task_id=task.task_id,
                knowledge_type="ARCHITECTURE",
                title="System Architecture Overview",
                understanding="The system uses a layered architecture with domain-driven design principles and clean separation of concerns",
                confidence=0.9,
            )
            r1.adapter.learn(learning)
            r1.adapter.complete_task(task.task_id)
            versions = r1.repository.list_all_versions()
            assert len(versions) == 1
            identity_id = versions[0].identity_id

            del r1
            gc.collect()

            r2 = create_sqlite_runtime(path)
            retrieved = r2.service.history(identity_id)
            assert len(retrieved) == 1
            assert retrieved[0].title == "System Architecture Overview"
            del r2
            gc.collect()
        finally:
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except PermissionError:
                    pass
