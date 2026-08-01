from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class AuthorizationToken:
    """
    The constitutional artifact consumed by future Execution.

    Execution must consume AuthorizationToken.
    Execution must never consume GovernanceDecision directly.

    This object represents constitutional permission only.
    It contains no execution metadata.
    """

    token_id: uuid.UUID
    authorization_record_id: uuid.UUID
    issued_at: datetime
    constitutional_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")