import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.retrieval.condition import TriggerCondition


@dataclass(frozen=True)
class RetrievalTrigger:
    name: str
    description: str
    condition: TriggerCondition
    priority: int = 0
    enabled: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if self.priority < 0:
            raise ValueError("priority must be >= 0")
