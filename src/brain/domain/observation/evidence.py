from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass(frozen=True)
class ObservationEvidence:
    """
    Supporting evidence for an observation.

    Explains WHY the observation exists without interpreting meaning.

    Examples:
    - "Sample: 100 executions over 24h, failure rate 0.05"
    - "Measurement period: 2026-01-15T00:00 to 2026-01-16T00:00"
    - "Reliability: 0.95 (based on consistent measurement method)"

    Does NOT:
    - Interpret meaning
    - Recommend actions
    - Assign severity
    """

    evidence_id: uuid.UUID = uuid.uuid4()
    description: str = ""
    sample_count: int = 0
    measurement_start: datetime = datetime.now(timezone.utc)
    measurement_end: datetime = datetime.now(timezone.utc)
    confidence: float = 0.0
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if self.sample_count < 0:
            raise ValueError("sample_count must be non-negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.measurement_end < self.measurement_start:
            raise ValueError("measurement_end must not be before measurement_start")