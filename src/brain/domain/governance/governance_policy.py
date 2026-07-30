from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class GovernancePolicy:
    """
    Immutable constitutional rule.

    Policies are read-only constitutional constraints.
    Governance interprets policies; it never modifies them.
    """

    policy_id: uuid.UUID = uuid.uuid4()
    identifier: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    governing_principle: str = ""
    version: str = "1.0"
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier must not be empty")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.governing_principle.strip():
            raise ValueError("governing_principle must not be empty")