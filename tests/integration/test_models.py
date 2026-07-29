import uuid

import pytest

from brain.integration.models import IntegrationContext, IntegrationLearning, IntegrationSection, IntegrationTask


class TestIntegrationTask:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        task = IntegrationTask(
            task_id=task_id,
            objective="Fix bug",
            project="atlas",
            component="auth",
            task_type="DEBUG",
        )
        assert task.task_id == task_id
        assert task.objective == "Fix bug"
        assert task.project == "atlas"
        assert task.component == "auth"
        assert task.task_type == "DEBUG"
        assert task.metadata == ()

    def test_with_metadata(self) -> None:
        metadata = (("key", "val"),)
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Fix",
            project="atlas",
            component="auth",
            task_type="DEBUG",
            metadata=metadata,
        )
        assert task.metadata == metadata

    def test_empty_objective_raises(self) -> None:
        with pytest.raises(ValueError, match="objective must not be empty"):
            IntegrationTask(
                task_id=uuid.uuid4(),
                objective="",
                project="atlas",
                component="auth",
                task_type="DEBUG",
            )

    def test_empty_project_raises(self) -> None:
        with pytest.raises(ValueError, match="project must not be empty"):
            IntegrationTask(
                task_id=uuid.uuid4(),
                objective="Fix",
                project="",
                component="auth",
                task_type="DEBUG",
            )

    def test_empty_component_raises(self) -> None:
        with pytest.raises(ValueError, match="component must not be empty"):
            IntegrationTask(
                task_id=uuid.uuid4(),
                objective="Fix",
                project="atlas",
                component="",
                task_type="DEBUG",
            )

    def test_frozen(self) -> None:
        task = IntegrationTask(
            task_id=uuid.uuid4(),
            objective="Fix",
            project="atlas",
            component="auth",
            task_type="DEBUG",
        )
        with pytest.raises(AttributeError):
            task.objective = "new"  # type: ignore[misc]


class TestIntegrationContext:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        ctx = IntegrationContext(task_id=task_id, sections=())
        assert ctx.task_id == task_id
        assert ctx.sections == ()
        assert ctx.generated_at is not None

    def test_with_sections(self) -> None:
        section = IntegrationSection(
            section_type="architecture",
            title="Architecture",
            content=("Auth service",),
        )
        ctx = IntegrationContext(
            task_id=uuid.uuid4(),
            sections=(section,),
        )
        assert len(ctx.sections) == 1
        assert ctx.sections[0].title == "Architecture"

    def test_frozen(self) -> None:
        ctx = IntegrationContext(task_id=uuid.uuid4(), sections=())
        with pytest.raises(AttributeError):
            ctx.task_id = uuid.uuid4()  # type: ignore[misc]


class TestIntegrationSection:
    def test_creation(self) -> None:
        section = IntegrationSection(
            section_type="bugs",
            title="Known Issues",
            content=("Login timeout",),
        )
        assert section.section_type == "bugs"
        assert section.title == "Known Issues"
        assert section.content == ("Login timeout",)

    def test_frozen(self) -> None:
        section = IntegrationSection(
            section_type="test",
            title="Test",
            content=(),
        )
        with pytest.raises(AttributeError):
            section.title = "new"  # type: ignore[misc]


class TestIntegrationLearning:
    def test_creation(self) -> None:
        task_id = uuid.uuid4()
        learning = IntegrationLearning(
            task_id=task_id,
            knowledge_type="ARCHITECTURE",
            title="Auth Design",
            understanding="OAuth2 flow",
            confidence=0.9,
        )
        assert learning.task_id == task_id
        assert learning.knowledge_type == "ARCHITECTURE"
        assert learning.title == "Auth Design"
        assert learning.confidence == 0.9

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValueError, match="title must not be empty"):
            IntegrationLearning(
                task_id=uuid.uuid4(),
                knowledge_type="BUG",
                title="",
                understanding="test",
                confidence=0.5,
            )

    def test_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence must be between"):
            IntegrationLearning(
                task_id=uuid.uuid4(),
                knowledge_type="BUG",
                title="test",
                understanding="test",
                confidence=1.5,
            )

    def test_negative_confidence_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence must be between"):
            IntegrationLearning(
                task_id=uuid.uuid4(),
                knowledge_type="BUG",
                title="test",
                understanding="test",
                confidence=-0.1,
            )

    def test_frozen(self) -> None:
        learning = IntegrationLearning(
            task_id=uuid.uuid4(),
            knowledge_type="BUG",
            title="test",
            understanding="test",
            confidence=0.5,
        )
        with pytest.raises(AttributeError):
            learning.title = "new"  # type: ignore[misc]
