from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    IMPLEMENT = "implement"
    DEBUG = "debug"
    REFACTOR = "refactor"
    REVIEW = "review"
    TEST = "test"
    DOCUMENT = "document"
    OPTIMIZE = "optimize"
    INTEGRATE = "integrate"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class Task:
    task_type: TaskType
    project: str
    component: str
    objective: str
    constraints: tuple[str, ...]
    priority: Priority

    def __post_init__(self) -> None:
        if not self.project.strip():
            raise ValueError("project must not be empty")
        if not self.component.strip():
            raise ValueError("component must not be empty")
        if not self.objective.strip():
            raise ValueError("objective must not be empty")
