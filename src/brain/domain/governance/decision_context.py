from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class DecisionContext:
    """
    The ONLY information Governance may access.

    This prevents hidden dependencies and ensures Governance
    makes decisions based solely on constitutional inputs.

    Governance may NOT access:
    - Runtime state
    - Repository data
    - Execution context
    - Optimization data
    - External systems
    """

    evaluation_id: uuid.UUID
    created_at: datetime
    proposal_ids: tuple = ()
    policy_ids: tuple = ()
    constitutional_version: str = ""
    metadata: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")