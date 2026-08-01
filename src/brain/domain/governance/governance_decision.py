from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from brain.domain.governance.enums import DecisionState


@dataclass(frozen=True)
class GovernanceDecision:
    """
    The constitutional outcome of evaluating an Evaluation.

    A GovernanceDecision is the constitutional authority's determination.
    It contains NO execution logic, NO mutation, NO proposal generation.

    Constitutional Laws Enforced:
    - G-1: Governance consumes Evaluation only.
    - G-2: Governance never evaluates.
    - G-3: Governance never creates proposals.
    - G-4: Governance never executes.
    - G-5: Every decision references explicit evidence.
    - G-6: Every decision references constitutional policies.
    - G-7: Governance is deterministic.
    - G-8: Governance may defer decisions.
    - G-11: Governance never mutates Evaluation.
    - G-12: Governance never mutates Proposal.
    - G-13: One active decision per Evaluation.
    - G-14: Decision history is immutable.
    - G-15: Constitution overrides optimization.
    - G-16: Governance never bypasses constitutional policy.
    - G-18: Governance owns decisions only.
    - G-19: Governance never performs optimization.
    - G-20: Decision and Rationale are separate.
    - G-21: Policies are immutable.
    - G-22: Deterministic outcomes.
    - G-23: Governance never creates constitutional rules.
    """

    decision_id: uuid.UUID
    evaluation_id: uuid.UUID
    created_at: datetime
    rationale_id: uuid.UUID
    state: str = "requires_review"  # DecisionState value as string
    policy_ids: tuple = ()
    superseded_by: uuid.UUID | None = None

    def __post_init__(self) -> None:
        pass

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None