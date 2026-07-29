import uuid
from dataclasses import dataclass, field
from enum import Enum

from brain.domain.enums import KnowledgeType


class ActionStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Action:
    goal_id: uuid.UUID
    title: str
    description: str
    required_knowledge: tuple[KnowledgeType, ...] = ()
    dependencies: tuple[uuid.UUID, ...] = ()
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: ActionStatus = ActionStatus.PENDING

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description or not self.description.strip():
            raise ValueError("description must not be empty")
