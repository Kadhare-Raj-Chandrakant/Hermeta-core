import uuid

import pytest

from brain.adapter.models import AdapterContext, AdapterLearning, AdapterTask
from brain.domain.task import TaskType
from brain.services.compiler import ContextPackage
from brain.domain.task import Task, Priority


def _make_adapter_task(**overrides) -> AdapterTask:
    defaults = dict(
        task_id=uuid.uuid4(),
        task_type=TaskType.IMPLEMENT,
        objective="Implement login",
        project="atlas",
        component="auth",
    )
    defaults.update(overrides)
    return AdapterTask(**defaults)


def _make_context_package() -> ContextPackage:
    task = Task(
        task_type=TaskType.IMPLEMENT,
        project="atlas",
        component="auth",
        objective="test",
        constraints=(),
        priority=Priority.MEDIUM,
    )
    return ContextPackage(task=task, sections=())


class TestAdapterTask:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        task = AdapterTask(
            task_id=task_id,
            task_type=TaskType.DEBUG,
            objective="Fix bug",
            project="atlas",
            component="auth",
        )
        assert task.task_id == task_id
        assert task.task_type == TaskType.DEBUG
        assert task.objective == "Fix bug"
        assert task.project == "atlas"
        assert task.component == "auth"
        assert task.metadata == ()
        assert task.created_at is not None

    def test_with_metadata(self) -> None:
        metadata = (("key1", "val1"), ("key2", "val2"))
        task = AdapterTask(
            task_id=uuid.uuid4(),
            task_type=TaskType.IMPLEMENT,
            objective="Fix bug",
            project="atlas",
            component="auth",
            metadata=metadata,
        )
        assert task.metadata == metadata

    def test_empty_objective_raises(self) -> None:
        with pytest.raises(ValueError, match="objective must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="",
                project="atlas",
                component="auth",
            )

    def test_whitespace_objective_raises(self) -> None:
        with pytest.raises(ValueError, match="objective must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="   ",
                project="atlas",
                component="auth",
            )

    def test_empty_project_raises(self) -> None:
        with pytest.raises(ValueError, match="project must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="Fix bug",
                project="",
                component="auth",
            )

    def test_whitespace_project_raises(self) -> None:
        with pytest.raises(ValueError, match="project must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="Fix bug",
                project="   ",
                component="auth",
            )

    def test_empty_component_raises(self) -> None:
        with pytest.raises(ValueError, match="component must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="Fix bug",
                project="atlas",
                component="",
            )

    def test_whitespace_component_raises(self) -> None:
        with pytest.raises(ValueError, match="component must not be empty"):
            AdapterTask(
                task_id=uuid.uuid4(),
                task_type=TaskType.IMPLEMENT,
                objective="Fix bug",
                project="atlas",
                component="   ",
            )

    def test_frozen(self) -> None:
        task = _make_adapter_task()
        with pytest.raises(AttributeError):
            task.objective = "new"  # type: ignore[misc]


class TestAdapterContext:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        ctx = AdapterContext(
            task_id=task_id,
            context=_make_context_package(),
        )
        assert ctx.task_id == task_id
        assert ctx.generated_at is not None

    def test_frozen(self) -> None:
        ctx = AdapterContext(
            task_id=uuid.uuid4(),
            context=_make_context_package(),
        )
        with pytest.raises(AttributeError):
            ctx.task_id = uuid.uuid4()  # type: ignore[misc]


class TestAdapterLearning:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        learning = AdapterLearning(
            task_id=task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth Architecture",
            understanding="OAuth2 flow",
            confidence=0.9,
        )
        assert learning.task_id == task_id
        assert learning.knowledge_type == "ARCHITECTURE"
        assert learning.title == "Auth Architecture"
        assert learning.understanding == "OAuth2 flow"
        assert learning.confidence == 0.9
        assert learning.submitted_at is not None

    def test_frozen(self) -> None:
        learning = AdapterLearning(
            task_id=uuid.uuid4(),
            knowledge_type="BUG",
            title="test",
            understanding="test",
            confidence=0.5,
        )
        with pytest.raises(AttributeError):
            learning.task_id = uuid.uuid4()  # type: ignore[misc]

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValueError, match="title must not be empty"):
            AdapterLearning(
                task_id=uuid.uuid4(),
                knowledge_type="BUG",
                title="",
                understanding="test",
                confidence=0.5,
            )

    def test_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence must be between"):
            AdapterLearning(
                task_id=uuid.uuid4(),
                knowledge_type="BUG",
                title="test",
                understanding="test",
                confidence=1.5,
            )
