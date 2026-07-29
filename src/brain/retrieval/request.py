import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task


@dataclass(frozen=True)
class RetrievalRequest:
    task: Task
    trigger_ids: tuple[uuid.UUID, ...]
    knowledge_types: tuple[KnowledgeType, ...]
    reason: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("reason must not be empty")
