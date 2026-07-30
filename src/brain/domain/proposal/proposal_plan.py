from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.proposal.enums import ProposalCategory, RiskLevel


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