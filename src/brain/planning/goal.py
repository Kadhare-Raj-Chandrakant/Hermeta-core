import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from brain.domain.task import Priority


class GoalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"


@dataclass(frozen=True)
class Goal:
    title: str
    description: str
    project: str
    priority: Priority
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: GoalStatus = GoalStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description or not self.description.strip():
            raise ValueError("description must not be empty")
        if not self.project or not self.project.strip():
            raise ValueError("project must not be empty")
