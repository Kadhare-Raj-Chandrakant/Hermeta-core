import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ExecutionContext:
    plan_id: uuid.UUID
    project: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
