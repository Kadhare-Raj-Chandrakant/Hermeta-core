from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.reflection.type import ReflectionType


@dataclass(frozen=True)
class ReflectionFinding:
    reflection_type: ReflectionType
    affected_versions: tuple[uuid.UUID, ...]
    explanation: str
    confidence: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.explanation or not self.explanation.strip():
            raise ValueError("explanation must not be empty")
        if not isinstance(self.affected_versions, tuple):
            raise ValueError("affected_versions must be a tuple")
