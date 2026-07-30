from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionHistory:
    """
    Immutable append-only record of all execution activities.

    History is never overwritten. Supersession creates a new record.
    History owns archival responsibility only.

    It must never expose behavior such as:
    - execute()
    - latest()
    - activate()
    - execute()
    """

    history_id: uuid.UUID = uuid.uuid4()
    execution_result_ids: tuple = ()
    constitutional_version: str = "1.0"
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")

    @property
    def execution_count(self) -> int:
        return len(self.execution_result_ids)

    def with_result(self, result_id: uuid.UUID) -> "ExecutionHistory":
        """Return a new history with the result appended (immutable append)."""
        return ExecutionHistory(
            history_id=uuid.uuid4(),
            execution_result_ids=self.execution_result_ids + (result_id,),
            constitutional_version=self.constitutional_version,
            created_at=self.created_at,
        )