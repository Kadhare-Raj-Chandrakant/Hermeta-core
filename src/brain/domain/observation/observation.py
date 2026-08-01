from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

from brain.domain.observation.signal import ObservationSignal, SignalCategory
from brain.domain.observation.evidence import ObservationEvidence


class ObservationCategory(Enum):
    """
    Categories describe the ORIGIN of an observation.

    They do NOT represent:
    - Severity
    - Urgency
    - Required action
    - Priority
    """

    OPERATIONAL = "operational"
    COGNITIVE = "cognitive"
    EVOLUTION_HISTORY = "evolution_history"


@dataclass(frozen=True)
class SystemObservation:
    """
    One Hermes self-observation.

    Represents: "What Hermes knows about its own state at a moment."

    Contains:
    - What was observed (signal)
    - Why it was observed (evidence)
    - Confidence in the observation
    - When it was observed

    Does NOT contain:
    - should_change / requires_action
    - recommended_action / solution
    - decision / proposal
    - evaluation / diagnosis
    """

    observation_id: uuid.UUID
    timestamp: datetime
    target: str = ""
    category: ObservationCategory = ObservationCategory.OPERATIONAL
    signal: ObservationSignal | None = None
    evidence: ObservationEvidence | None = None
    confidence: float = 0.0
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("target must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")

    @property
    def has_signal(self) -> bool:
        return self.signal is not None

    @property
    def has_evidence(self) -> bool:
        return self.evidence is not None