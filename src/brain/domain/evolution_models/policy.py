from dataclasses import dataclass
from enum import Enum
import uuid


class ApprovalMode(Enum):
    AUTOMATIC = "automatic"
    HUMAN_REQUIRED = "human_required"
    QUORUM_REQUIRED = "quorum_required"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class EvolutionPolicy:
    approval_mode: ApprovalMode
    risk_level: RiskLevel
    max_operations_per_plan: int = 10
    require_impact_analysis: bool = True
    require_rollback_plan: bool = True
    allowed_intent_types: tuple[str, ...] = ()
    quarantined_identities: tuple[uuid.UUID, ...] = ()

    def __post_init__(self) -> None:
        if self.max_operations_per_plan <= 0:
            raise ValueError("max_operations_per_plan must be positive")