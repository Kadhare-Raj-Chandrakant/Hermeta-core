from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship


@dataclass(frozen=True)
class KnowledgeVersion:
    identity_id: uuid.UUID
    version_id: uuid.UUID = field(default_factory=uuid.uuid4)
    version_number: int = 1
    knowledge_type: KnowledgeType = KnowledgeType.DISCOVERY
    title: str = ""
    understanding: str = ""
    confidence: float = 0.0
    lifecycle_state: LifecycleState = LifecycleState.DRAFT
    evidence: tuple[Evidence, ...] = ()
    relationships: tuple[Relationship, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.version_number < 1:
            raise ValueError(f"Version number must be >= 1, got {self.version_number}")
