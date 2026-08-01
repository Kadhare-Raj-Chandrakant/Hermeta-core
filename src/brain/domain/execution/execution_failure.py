from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionFailure:
    """
    An observed execution failure.

    Failures are facts — not recommendations, not recovery plans.
    They are evidence only.
    """

    failure_id: uuid.UUID
    timestamp: datetime
    related_plan_id: uuid.UUID
    related_result_id: uuid.UUID
    failure_type: str = ""
    observed_error: str = ""

    def __post_init__(self) -> None:
        if not self.failure_type.strip():
            raise ValueError("failure_type must not be empty")
        if not self.observed_error.strip():
            raise ValueError("observed_error must not be empty")