import pytest

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.retrieval.conditions.component import ComponentCondition
from brain.retrieval.conditions.keyword import KeywordCondition
from brain.retrieval.conditions.knowledge_type import KnowledgeTypeCondition
from brain.retrieval.conditions.project import ProjectCondition
from brain.retrieval.conditions.task_type import TaskTypeCondition


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


class TestTaskTypeCondition:
    def test_matching(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT, TaskType.DEBUG))
        task = _make_task(task_type=TaskType.IMPLEMENT)
        assert condition.matches(task) is True

    def test_non_matching(self) -> None:
        condition = TaskTypeCondition((TaskType.IMPLEMENT,))
        task = _make_task(task_type=TaskType.DEBUG)
        assert condition.matches(task) is False

    def test_single_type(self) -> None:
        condition = TaskTypeCondition((TaskType.REFACTOR,))
        task = _make_task(task_type=TaskType.REFACTOR)
        assert condition.matches(task) is True

    def test_empty_types(self) -> None:
        condition = TaskTypeCondition(())
        task = _make_task()
        assert condition.matches(task) is False

    def test_task_types_property(self) -> None:
        types = (TaskType.IMPLEMENT, TaskType.DEBUG)
        condition = TaskTypeCondition(types)
        assert condition.task_types == types


class TestKnowledgeTypeCondition:
    def test_always_matches(self) -> None:
        condition = KnowledgeTypeCondition((KnowledgeType.ARCHITECTURE,))
        task = _make_task()
        assert condition.matches(task) is True

    def test_matches_any_task_type(self) -> None:
        condition = KnowledgeTypeCondition((KnowledgeType.DECISION,))
        task = _make_task(task_type=TaskType.DEBUG)
        assert condition.matches(task) is True

    def test_knowledge_types_property(self) -> None:
        types = (KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT)
        condition = KnowledgeTypeCondition(types)
        assert condition.knowledge_types == types


class TestProjectCondition:
    def test_matching(self) -> None:
        condition = ProjectCondition(("atlas",))
        task = _make_task(project="atlas")
        assert condition.matches(task) is True

    def test_non_matching(self) -> None:
        condition = ProjectCondition(("atlas",))
        task = _make_task(project="hermes")
        assert condition.matches(task) is False

    def test_multiple_projects(self) -> None:
        condition = ProjectCondition(("atlas", "hermes"))
        task = _make_task(project="hermes")
        assert condition.matches(task) is True

    def test_empty_projects(self) -> None:
        condition = ProjectCondition(())
        task = _make_task()
        assert condition.matches(task) is False

    def test_projects_property(self) -> None:
        projects = ("atlas", "hermes")
        condition = ProjectCondition(projects)
        assert condition.projects == projects


class TestComponentCondition:
    def test_matching(self) -> None:
        condition = ComponentCondition(("auth",))
        task = _make_task(component="auth")
        assert condition.matches(task) is True

    def test_non_matching(self) -> None:
        condition = ComponentCondition(("auth",))
        task = _make_task(component="database")
        assert condition.matches(task) is False

    def test_multiple_components(self) -> None:
        condition = ComponentCondition(("auth", "api"))
        task = _make_task(component="api")
        assert condition.matches(task) is True

    def test_empty_components(self) -> None:
        condition = ComponentCondition(())
        task = _make_task()
        assert condition.matches(task) is False

    def test_components_property(self) -> None:
        components = ("auth", "api")
        condition = ComponentCondition(components)
        assert condition.components == components


class TestKeywordCondition:
    def test_matching(self) -> None:
        condition = KeywordCondition(("login",))
        task = _make_task(objective="Implement login flow")
        assert condition.matches(task) is True

    def test_non_matching(self) -> None:
        condition = KeywordCondition(("database",))
        task = _make_task(objective="Implement login flow")
        assert condition.matches(task) is False

    def test_case_insensitive(self) -> None:
        condition = KeywordCondition(("LOGIN",))
        task = _make_task(objective="implement login flow")
        assert condition.matches(task) is True

    def test_case_insensitive_mixed(self) -> None:
        condition = KeywordCondition(("LoGiN",))
        task = _make_task(objective="IMPLEMENT LOGIN FLOW")
        assert condition.matches(task) is True

    def test_multiple_keywords(self) -> None:
        condition = KeywordCondition(("login", "auth"))
        task = _make_task(objective="Implement authentication")
        assert condition.matches(task) is True

    def test_empty_keywords(self) -> None:
        condition = KeywordCondition(())
        task = _make_task()
        assert condition.matches(task) is False

    def test_keyword_in_objective_only(self) -> None:
        condition = KeywordCondition(("auth",))
        task = _make_task(component="auth", objective="Implement login")
        assert condition.matches(task) is False

    def test_keywords_property(self) -> None:
        keywords = ("login", "auth")
        condition = KeywordCondition(keywords)
        assert condition.keywords == keywords
