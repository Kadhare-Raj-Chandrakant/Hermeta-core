from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid

from brain.domain.execution.enums import ExecutionStatus, ArtifactType, FailureType


@dataclass(frozen=True)
class ExecutionResult:
    """
    The observable outcome of execution.

    An ExecutionResult is a FACT, not a judgment.
    It records what happened, not what should happen next.

    Constitutional Laws Enforced:
    - X-11: Execution produces only observable facts.
    - X-12: Execution produces ExecutionReceipt as primary artifact.
    - X-13: ExecutionResult never contains recommendations.
    - X-14: ExecutionResult never contains evaluations.
    - X-15: ExecutionResult never contains governance decisions.
    - X-16: ExecutionResult never contains authorization states.
    - X-17: ExecutionResult contains only observable facts.
    """

    execution_result_id: uuid.UUID
    execution_plan_id: uuid.UUID
    authorization_token_id: uuid.UUID
    status: str = "pending"  # ExecutionStatus value

    # Observable facts only
    artifacts_produced: tuple = ()
    artifact_ids: tuple = ()
    error_report: Optional[str] = None
    failure_type: Optional[str] = None  # FailureType value
    duration_ms: int = 0
    metrics: tuple = ()
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.execution_plan_id:
            raise ValueError("execution_plan_id must not be empty")

    @property
    def is_terminal(self) -> bool:
        return self.status in (
            "completed", "failed", "withdrawn", "superseded"
        )

    @property
    def is_successful(self) -> bool:
        return self.status == "completed"