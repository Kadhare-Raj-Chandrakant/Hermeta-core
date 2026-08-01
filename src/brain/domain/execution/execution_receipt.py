from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionReceipt:
    """
    The primary constitutional artifact produced by execution.

    An ExecutionReceipt is the ONLY artifact that execution is required
    to produce. It is a receipt, not a report. It proves execution occurred
    and records what was observed.

    Constitutional Laws Enforced:
    - X-12: Execution produces ExecutionReceipt as primary artifact.
    - X-22: ExecutionReceipt is the only artifact Execution is required to produce.
    - X-23: ExecutionReceipt is an observable fact for future Observation.
    """

    receipt_id: uuid.UUID
    execution_result_id: uuid.UUID
    authorization_token_id: uuid.UUID
    issued_at: datetime
    constitutional_version: str = "1.0"

    # Observable facts recorded
    execution_duration_ms: int = 0
    artifact_count: int = 0
    status_at_completion: str = "unknown"
    metrics_hash: str = ""

    def __post_init__(self) -> None:
        if not self.execution_result_id:
            raise ValueError("execution_result_id must not be empty")