from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class EvolutionRecord:
    plan_identity: uuid.UUID
    executed_at: datetime
    success: bool
    operations_count: int
    affected_targets: tuple[uuid.UUID, ...]
    reason: str = ""
    policy: str = ""


@dataclass(frozen=True)
class ExecutionFailureRecord:
    plan_identity: uuid.UUID
    executed_at: datetime
    failure_reason: str
    failed_operation_index: int
    operations_count: int
    failure_type: str
    affected_targets: tuple[uuid.UUID, ...] = ()
    policy: str = ""


class OptimisticConcurrencyError(Exception):
    def __init__(
        self,
        operation_index: int,
        target_id: uuid.UUID,
        expected_version_id: uuid.UUID,
        actual_version_id: uuid.UUID,
    ) -> None:
        self.operation_index = operation_index
        self.target_id = target_id
        self.expected_version_id = expected_version_id
        self.actual_version_id = actual_version_id
        super().__init__(
            f"Operation {operation_index}: expected version {expected_version_id} "
            f"for target {target_id}, but found {actual_version_id}"
        )
