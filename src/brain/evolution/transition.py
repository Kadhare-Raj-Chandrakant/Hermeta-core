from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.evolution.transition_type import TransitionType


@dataclass(frozen=True)
class KnowledgeTransition:
    from_version_id: uuid.UUID
    to_version_id: uuid.UUID
    transition_type: TransitionType
    reason: str
    confidence: float
    source: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.reason or not self.reason.strip():
            raise ValueError("reason must not be empty")
        if not self.source or not self.source.strip():
            raise ValueError("source must not be empty")
