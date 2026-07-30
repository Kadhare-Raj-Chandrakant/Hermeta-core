from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class GovernanceHistory:
    """
    Immutable record of every governance decision.

    History is never overwritten. Supersession creates a new record.
    Every decision is preserved for audit and future reasoning.
    """

    history_id: uuid.UUID = uuid.uuid4()
    decision_ids: tuple = field(default_factory=tuple)
    constitutional_version: str = "1.0"
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")

    @property
    def decision_count(self) -> int:
        return len(self.decision_ids)

    def with_decision(self, decision_id: uuid.UUID) -> "GovernanceHistory":
        """Return a new history with the decision added (immutable)."""
        return GovernanceHistory(
            history_id=uuid.uuid4(),
            decision_ids=self.decision_ids + (decision_id,),
            constitutional_version=self.constitutional_version,
            created_at=self.created_at,
        )