from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class GovernanceRationale:
    """
    WHY a decision exists.

    Contains explanation and reasoning ONLY.
    Contains NO authority. Contains NO decision state.

    Authority belongs to GovernanceDecision.
    """

    rationale_id: uuid.UUID
    created_at: datetime
    explanation: str = ""
    supporting_evidence_ids: tuple = ()
    constitutional_interpretations: tuple = ()
    constitutional_basis: tuple = ()
    findings: tuple = ()

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("explanation must not be empty")