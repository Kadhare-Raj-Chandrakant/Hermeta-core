from dataclasses import dataclass
from enum import Enum
import uuid


class TriggerType(Enum):
    REFLECTION_FINDING = "reflection_finding"
    KNOWLEDGE_GAP = "knowledge_gap"
    CONFLICT_DETECTED = "conflict_detected"
    OBSOLESCENCE_DETECTED = "obsolescence_detected"
    DUPLICATE_DETECTED = "duplicate_detected"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    USER_REQUEST = "user_request"
    SCHEDULED_REVIEW = "scheduled_review"


@dataclass(frozen=True)
class EvolutionTrigger:
    trigger_type: TriggerType
    source_identity: uuid.UUID
    description: str
    confidence: float
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.description.strip():
            raise ValueError("description must not be empty")