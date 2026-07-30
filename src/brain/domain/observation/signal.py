from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class SignalCategory(Enum):
    OPERATIONAL = "operational"
    COGNITIVE = "cognitive"
    EVOLUTION_HISTORY = "evolution_history"


@dataclass(frozen=True)
class ObservationSignal:
    """
    A single measured fact about Hermes internal state.

    Examples:
    - "Execution failure count increased from 2 to 5 in last hour"
    - "Reflection finding count: 3 duplicates, 1 conflict"
    - "Knowledge repository size: 1,247 versions"

    Contains NO:
    - Recommendations
    - Decisions
    - Solutions
    - Interpretations
    """

    signal_id: uuid.UUID = uuid.uuid4()
    category: SignalCategory = SignalCategory.OPERATIONAL
    source: str = ""
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source must not be empty")
        if not self.metric_name.strip():
            raise ValueError("metric_name must not be empty")