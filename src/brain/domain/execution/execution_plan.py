from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionPlan:
    """
    One immutable execution instruction.

    An ExecutionPlan represents what has been authorized to execute.
    It contains NO reasoning, NO scheduling, NO optimization logic.

    Constitutional Laws Enforced:
    - X-1: Execution consumes AuthorizationToken only.
    - X-2: Execution performs only approved work.
    - X-3: Execution never reasons.
    - X-4: Execution never evaluates.
    - X-5: Execution never governs.
    - X-6: Execution never authorizes.
    - X-8: Execution never invents additional work.
    - X-9: Execution never expands execution scope.
    - X-10: Execution never modifies ExecutionPlan.
    - X-18: Execution is immutable.
    """

    execution_plan_id: uuid.UUID
    authorization_token_id: uuid.UUID
    created_at: datetime
    operation_identifier: str = ""
    required_inputs: tuple = ()
    constitutional_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.operation_identifier.strip():
            raise ValueError("operation_identifier must not be empty")