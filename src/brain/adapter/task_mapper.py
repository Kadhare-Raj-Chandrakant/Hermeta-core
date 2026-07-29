from brain.adapter.errors import InvalidAdapterTaskError
from brain.adapter.models import AdapterTask
from brain.domain.task import Task, TaskType, Priority

SUPPORTED_TASK_TYPES: frozenset[TaskType] = frozenset({
    TaskType.IMPLEMENT,
    TaskType.DEBUG,
    TaskType.REFACTOR,
    TaskType.REVIEW,
    TaskType.TEST,
    TaskType.DOCUMENT,
    TaskType.OPTIMIZE,
    TaskType.INTEGRATE,
})


class TaskMapper:
    def map(self, adapter_task: AdapterTask) -> Task:
        if adapter_task.task_type not in SUPPORTED_TASK_TYPES:
            raise InvalidAdapterTaskError(
                f"Unsupported task type: {adapter_task.task_type}"
            )
        return Task(
            task_type=adapter_task.task_type,
            project=adapter_task.project,
            component=adapter_task.component,
            objective=adapter_task.objective,
            constraints=(),
            priority=Priority.MEDIUM,
        )
