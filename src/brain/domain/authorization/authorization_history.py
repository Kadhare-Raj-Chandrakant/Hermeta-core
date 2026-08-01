from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class AuthorizationHistory:
    """
    Immutable append-only history of every authorization decision.

    History is never overwritten. Supersession creates a new record.
    History owns archival responsibility only.

    It must never expose behavior such as:
    - authorize()
    - latest()
    - activate()
    - execute()
    """

    history_id: uuid.UUID
    created_at: datetime
    authorization_record_ids: tuple = field(default_factory=tuple)
    constitutional_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")

    @property
    def record_count(self) -> int:
        return len(self.authorization_record_ids)

    def with_record(self, record_id: uuid.UUID) -> "AuthorizationHistory":
        """Return a new history with the record added (immutable append)."""
        return AuthorizationHistory(
            history_id=uuid.uuid4(),
            authorization_record_ids=self.authorization_record_ids + (record_id,),
            constitutional_version=self.constitutional_version,
            created_at=self.created_at,
        )