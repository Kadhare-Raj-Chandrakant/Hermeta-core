from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class AuthorizationRationale:
    """
    WHY authorization was granted or denied.

    Contains explanation and reasoning ONLY.
    Contains NO authority. Contains NO permission state.

    Authority belongs to AuthorizationRecord.
    """

    rationale_id: uuid.UUID
    created_at: datetime
    explanation: str = ""
    supporting_findings: tuple = ()
    supporting_constraint_ids: tuple = ()
    constitutional_basis: tuple = ()

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("explanation must not be empty")