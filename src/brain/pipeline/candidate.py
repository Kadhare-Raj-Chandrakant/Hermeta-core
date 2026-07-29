from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence


@dataclass(frozen=True)
class KnowledgeCandidate:
    knowledge_type: KnowledgeType
    title: str
    understanding: str
    confidence: float
    evidence_source: Evidence
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
