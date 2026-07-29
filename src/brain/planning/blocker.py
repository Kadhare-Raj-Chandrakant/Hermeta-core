import uuid
from dataclasses import dataclass, field
from enum import Enum


class BlockerSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Blocker:
    action_id: uuid.UUID
    description: str
    severity: BlockerSeverity
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("description must not be empty")
