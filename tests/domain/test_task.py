import pytest

from brain.domain.task import Priority, Task, TaskType


def create_task(
    task_type: TaskType = TaskType.IMPLEMENT,
    project: str = "hermes-brain",
    component: str = "domain",
    objective: str = "Add new feature",
    constraints: tuple[str, ...] = (),
    priority: Priority = Priority.MEDIUM,
) -> Task:
    return Task(
        task_type=task_type,
        project=project,
        component=component,
        objective=objective,
        constraints=constraints,
        priority=priority,
    )


class TestTaskImmutability:
    def test_task_is_frozen(self):
        task = create_task()
        with pytest.raises(AttributeError):
            task.project = "other"

    def test_task_type_is_frozen(self):
        task = create_task()
        with pytest.raises(AttributeError):
            task.task_type = TaskType.DEBUG

    def test_objective_is_frozen(self):
        task = create_task()
        with pytest.raises(AttributeError):
            task.objective = "new objective"

    def test_constraints_is_frozen(self):
        task = create_task()
        with pytest.raises(AttributeError):
            task.constraints = ()

    def test_priority_is_frozen(self):
        task = create_task()
        with pytest.raises(AttributeError):
            task.priority = Priority.HIGH


class TestTaskValidation:
    def test_empty_project_raises(self):
        with pytest.raises(ValueError, match="project"):
            create_task(project="")

    def test_whitespace_project_raises(self):
        with pytest.raises(ValueError, match="project"):
            create_task(project="   ")

    def test_empty_component_raises(self):
        with pytest.raises(ValueError, match="component"):
            create_task(component="")

    def test_whitespace_component_raises(self):
        with pytest.raises(ValueError, match="component"):
            create_task(component="   ")

    def test_empty_objective_raises(self):
        with pytest.raises(ValueError, match="objective"):
            create_task(objective="")

    def test_whitespace_objective_raises(self):
        with pytest.raises(ValueError, match="objective"):
            create_task(objective="   ")


class TestTaskEquality:
    def test_equal_tasks(self):
        t1 = Task(
            task_type=TaskType.IMPLEMENT,
            project="hermes-brain",
            component="domain",
            objective="Add feature",
            constraints=("no breaking changes",),
            priority=Priority.HIGH,
        )
        t2 = Task(
            task_type=TaskType.IMPLEMENT,
            project="hermes-brain",
            component="domain",
            objective="Add feature",
            constraints=("no breaking changes",),
            priority=Priority.HIGH,
        )
        assert t1 == t2

    def test_unequal_tasks(self):
        t1 = create_task(project="project-a")
        t2 = create_task(project="project-b")
        assert t1 != t2


class TestTaskTypeEnum:
    def test_all_types_exist(self):
        assert TaskType.IMPLEMENT.value == "implement"
        assert TaskType.DEBUG.value == "debug"
        assert TaskType.REFACTOR.value == "refactor"
        assert TaskType.REVIEW.value == "review"
        assert TaskType.TEST.value == "test"
        assert TaskType.DOCUMENT.value == "document"
        assert TaskType.OPTIMIZE.value == "optimize"
        assert TaskType.INTEGRATE.value == "integrate"

    def test_type_count(self):
        assert len(TaskType) == 8


class TestPriorityEnum:
    def test_all_priorities_exist(self):
        assert Priority.CRITICAL.value == "critical"
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_priority_count(self):
        assert len(Priority) == 4


class TestTaskTuples:
    def test_empty_constraints(self):
        task = create_task(constraints=())
        assert task.constraints == ()

    def test_multiple_constraints(self):
        task = create_task(constraints=("no breaking changes", "must be backward compatible"))
        assert len(task.constraints) == 2
        assert "no breaking changes" in task.constraints
