from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class ConflictStatus(Enum):
    OPEN = "open"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class Conflict:
    version_ids: tuple[uuid.UUID, ...]
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: ConflictStatus = ConflictStatus.OPEN
    resolution: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        if len(self.version_ids) < 2:
            raise ValueError("version_ids must contain at least two entries")
        if not self.description or not self.description.strip():
            raise ValueError("description must not be empty")
