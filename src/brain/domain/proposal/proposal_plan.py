from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class ProposalCategory(Enum):
    """
    Categories describe the TYPE of improvement a proposal represents.

    They do NOT represent:
    - Severity
    - Priority
    - Implementation effort
    - Risk level
    """

    ARCHITECTURAL = "architectural"
    ALGORITHMIC = "algorithmic"
    DATA_FLOW = "data_flow"
    INTERFACE = "interface"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"


class RiskLevel(Enum):
    """
    Risk levels represent POTENTIAL IMPACT of proposal execution.

    They do NOT represent:
    - Execution priority
    - Governance urgency
    - Resource allocation
    """

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionComplexity(Enum):
    """
    Complexity of executing the proposal.

    Does NOT represent:
    - Timeline
    - Cost
    - Staffing
    """

    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass(frozen=True)
class ProposalPlan:
    """
    A structured plan derived from a Proposal, ready for evaluation.

    A ProposalPlan translates the creative proposal into structured steps
    WITHOUT committing to execution. It is the bridge between Proposal
    and Evaluation.

    Constitutional Laws Enforced:
    - P-7: Plan is distinct from Proposal (creative → structured).
    - P-8: Plan contains no Evaluation, Decision, or Execution.
    - P-9: Plan references ProblemStatement traceability.
    """

    plan_id: uuid.UUID = uuid.uuid4()
    proposal_id: uuid.UUID = uuid.uuid4()
    steps: tuple[str, ...] = field(default_factory=tuple)
    affected_components: tuple[str, ...] = field(default_factory=tuple)
    rollback_steps: tuple[str, ...] = field(default_factory=tuple)
    prerequisites: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("steps must not be empty")
        if self.proposal_id is None:
            raise ValueError("proposal_id must not be None")

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def has_rollback(self) -> bool:
        return len(self.rollback_steps) > 0