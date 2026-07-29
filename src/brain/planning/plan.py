import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from brain.planning.action import Action
from brain.planning.blocker import Blocker
from brain.planning.dependency import Dependency
from brain.planning.goal import Goal


class PlanStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass(frozen=True)
class Plan:
    goal: Goal
    actions: tuple[Action, ...]
    dependencies: tuple[Dependency, ...]
    blockers: tuple[Blocker, ...]
    confidence: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
