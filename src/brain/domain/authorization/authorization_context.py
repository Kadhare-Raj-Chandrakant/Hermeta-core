from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class AuthorizationContext:
    """
    The ONLY information Authorization may access.

    Defines the constitutional boundary of authorization knowledge.
    Traceability already exists through GovernanceDecision.
    This context does NOT duplicate the full reasoning chain.
    """

    governance_decision_id: uuid.UUID
    created_at: datetime
    policy_ids: tuple = ()
    constitutional_version: str = ""
    metadata: tuple = ()

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")