import uuid

import pytest

from brain.adapter.errors import InvalidAdapterTaskError
from brain.adapter.models import AdapterTask
from brain.adapter.task_mapper import TaskMapper
from brain.domain.task import Task, TaskType


def _make_adapter_task(task_type: TaskType = TaskType.IMPLEMENT, **overrides) -> AdapterTask:
    defaults = dict(
        task_id=uuid.uuid4(),
        task_type=task_type,
        objective="Implement login",
        project="atlas",
        component="auth",
    )
    defaults.update(overrides)
    return AdapterTask(**defaults)


class TestTaskMapper:
    def test_implement_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.IMPLEMENT)
        result = mapper.map(task)
        assert isinstance(result, Task)
        assert result.task_type == TaskType.IMPLEMENT
        assert result.project == "atlas"
        assert result.component == "auth"
        assert result.objective == "Implement login"

    def test_debug_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.DEBUG)
        result = mapper.map(task)
        assert result.task_type == TaskType.DEBUG

    def test_refactor_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.REFACTOR)
        result = mapper.map(task)
        assert result.task_type == TaskType.REFACTOR

    def test_review_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.REVIEW)
        result = mapper.map(task)
        assert result.task_type == TaskType.REVIEW

    def test_test_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.TEST)
        result = mapper.map(task)
        assert result.task_type == TaskType.TEST

    def test_document_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.DOCUMENT)
        result = mapper.map(task)
        assert result.task_type == TaskType.DOCUMENT

    def test_optimize_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.OPTIMIZE)
        result = mapper.map(task)
        assert result.task_type == TaskType.OPTIMIZE

    def test_integrate_mapping(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task(task_type=TaskType.INTEGRATE)
        result = mapper.map(task)
        assert result.task_type == TaskType.INTEGRATE

    def test_all_task_types_supported(self) -> None:
        mapper = TaskMapper()
        for tt in TaskType:
            task = _make_adapter_task(task_type=tt)
            result = mapper.map(task)
            assert result.task_type == tt

    def test_empty_objective_rejected(self) -> None:
        mapper = TaskMapper()
        with pytest.raises(ValueError, match="objective must not be empty"):
            task = _make_adapter_task(objective="")
            mapper.map(task)

    def test_empty_project_rejected(self) -> None:
        mapper = TaskMapper()
        with pytest.raises(ValueError, match="project must not be empty"):
            task = _make_adapter_task(project="")
            mapper.map(task)

    def test_empty_component_rejected(self) -> None:
        mapper = TaskMapper()
        with pytest.raises(ValueError, match="component must not be empty"):
            task = _make_adapter_task(component="")
            mapper.map(task)

    def test_frozen_model(self) -> None:
        task = _make_adapter_task()
        with pytest.raises(AttributeError):
            task.objective = "new"  # type: ignore[misc]

    def test_mapper_returns_new_task(self) -> None:
        mapper = TaskMapper()
        task = _make_adapter_task()
        result1 = mapper.map(task)
        result2 = mapper.map(task)
        assert result1 is not result2
        assert result1 == result2
