from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class ExecutionStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ExecutionResult:
    plan_id: uuid.UUID
    status: ExecutionStatus
    executed_intents: tuple[uuid.UUID, ...]
    failed_intents: tuple[tuple[uuid.UUID, str], ...]
    started_at: datetime
    completed_at: datetime
    rollback_performed: bool = False
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.status == ExecutionStatus.SUCCESS and self.failed_intents:
            raise ValueError("SUCCESS status cannot have failed_intents")
        if self.status == ExecutionStatus.FAILED and not self.failed_intents:
            raise ValueError("FAILED status requires failed_intents")
        if self.rollback_performed and self.status not in (
            ExecutionStatus.FAILED,
            ExecutionStatus.PARTIAL,
            ExecutionStatus.ROLLED_BACK,
        ):
            raise ValueError("rollback_performed only valid for failure states")