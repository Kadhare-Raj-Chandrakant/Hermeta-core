from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class AuditEventType(Enum):
    TRIGGER_CREATED = "trigger_created"
    PLAN_PROPOSED = "plan_proposed"
    PLAN_APPROVED = "plan_approved"
    PLAN_REJECTED = "plan_rejected"
    PLAN_EXECUTED = "plan_executed"
    PLAN_ROLLED_BACK = "plan_rolled_back"
    POLICY_CHANGED = "policy_changed"
    QUARANTINE_ADDED = "quarantine_added"
    QUARANTINE_REMOVED = "quarantine_removed"


@dataclass(frozen=True)
class EvolutionAuditEntry:
    event_id: uuid.UUID
    event_type: AuditEventType
    timestamp: datetime
    actor: str
    plan_id: uuid.UUID | None = None
    trigger_id: uuid.UUID | None = None
    details: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.timestamp is None:
            raise ValueError("timestamp must be set")
        if not self.actor.strip():
            raise ValueError("actor must not be empty")