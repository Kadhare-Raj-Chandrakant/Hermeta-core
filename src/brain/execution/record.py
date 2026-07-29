import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.execution.status import ExecutionStatus


@dataclass(frozen=True)
class ExecutionRecord:
    action_id: uuid.UUID
    status: ExecutionStatus
    started_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.completed_at is not None and self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be before started_at")
