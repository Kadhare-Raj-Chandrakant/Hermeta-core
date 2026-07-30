from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionContext:
    """
    The ONLY information Execution may access.

    Defines the constitutional boundary of execution knowledge.
    Execution must not access:
    - Runtime state
    - Repository data
    - Authorization state beyond the token
    - Governance state
    - Evaluation state
    - Optimization data
    """

    execution_plan_id: uuid.UUID = uuid.uuid4()
    authorization_token_id: uuid.UUID = uuid.uuid4()
    constitutional_version: str = ""
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")