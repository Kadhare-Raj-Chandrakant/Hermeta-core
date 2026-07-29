from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence


@dataclass(frozen=True)
class KnowledgeEvent:
    event_type: KnowledgeType
    description: str
    evidence_source: Evidence
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("description must be a non-empty string")
