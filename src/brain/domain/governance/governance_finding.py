from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from brain.domain.governance.enums import FindingSeverity


@dataclass(frozen=True)
class GovernanceFinding:
    """
    One constitutional observation.

    Findings are observations about constitutional compliance.
    They never mutate anything. They are observations only.
    """

    finding_id: uuid.UUID
    created_at: datetime
    title: str = ""
    description: str = ""
    severity: str = "info"  # FindingSeverity value
    policy_ids: tuple = ()
    evidence_ids: tuple = ()

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")