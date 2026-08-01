from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from brain.domain.authorization.enums import AuthorizationState


@dataclass(frozen=True)
class AuthorizationRecord:
    """
    One immutable constitutional permission.

    Represents the constitutional permission derived from a GovernanceDecision.
    Contains only permission — no execution metadata, no runtime references,
    no scheduling, no workflow state.

    Constitutional Laws Enforced:
    - A-1: Authorization consumes GovernanceDecision only.
    - A-2: Authorization owns permission only.
    - A-3: Authorization never evaluates.
    - A-4: Authorization never governs.
    - A-5: Authorization never executes.
    - A-6: Authorization is immutable.
    - A-7: Authorization is deterministic.
    - A-8: Authorization is superseded, never mutated.
    - A-9: Authorization preserves traceability.
    - A-10: Authorization never bypasses Governance.
    - A-11: Authorization never invents permission.
    - A-12: Authorization never authorizes constitutional violations.
    - A-13: Authorization never weakens constitutional policy.
    - A-14: Authorization lifecycle is independent from execution lifecycle.
    - A-15: Execution consumes AuthorizationToken only.
    - A-16: Authorization contains no execution metadata.
    """

    authorization_id: uuid.UUID
    governance_decision_id: uuid.UUID
    rationale_id: uuid.UUID
    issued_at: datetime
    state: str = "requires_review"  # AuthorizationState value
    constitutional_version: str = "1.0"
    superseded_by: uuid.UUID | None = None

    def __post_init__(self) -> None:
        pass

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None