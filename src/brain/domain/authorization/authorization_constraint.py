from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class AuthorizationConstraint:
    """
    One constitutional restriction on authorization.

    Constraints are declarative restrictions — they never execute.
    They represent constitutional requirements that must be satisfied
    before authorization can be granted.

    Examples:
    - "human approval required for architectural changes"
    - "constitutional review required for evolution safety"
    - "evidence expired — re-evaluation required"
    - "authorization expired — re-authorization required"
    """

    constraint_id: uuid.UUID = uuid.uuid4()
    constraint_type: str = ""
    description: str = ""
    policy_ids: tuple = ()
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")