from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class EvolutionApproval:
    approval_id: uuid.UUID
    plan_id: uuid.UUID
    status: ApprovalStatus
    reviewer: str
    decided_at: datetime | None = None
    rationale: str = ""
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.status != ApprovalStatus.PENDING and self.decided_at is None:
            raise ValueError("decided_at required for non-pending status")
        if self.status == ApprovalStatus.REJECTED and not self.rationale.strip():
            raise ValueError("rejection requires rationale")