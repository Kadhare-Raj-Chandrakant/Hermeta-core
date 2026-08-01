from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.proposal.enums import ProposalCategory, ProposalState


@dataclass(frozen=True)
class Proposal:
    """
    A single candidate improvement.

    A Proposal is an IDEA, not a decision.

    Constitutional Laws Enforced:
    - P-1: A Proposal is an idea, not a decision. Never indicates approval/rejection.
    - P-2: Proposal expresses intent, not implementation. No code-level details.
    - P-3: Proposal never evaluates itself. No score/confidence/ranking/severity.
    - P-4: Proposal never mutates Hermes. No execution/mutation/runtime behavior.
    - P-5: Proposal remains completely traceable. Immutable traceability chain.
    - P-6: Proposal preserves uncertainty. Represents ONE possible improvement.
    - P-7: Proposal generation is creative, not analytical. No evaluation logic.
    - P-8: Proposal is unaware of Evaluation. No Evaluation/Decision/Execution references.
    - P-9: Proposal describes desired outcome. Not implementation mechanism.
    - P-10: Proposal categories represent cognitive intent. Not implementation.
    - P-11: Proposal models are immutable domain objects.
    """

    proposal_id: uuid.UUID
    originating_problem_id: uuid.UUID
    hypothesis_space_id: uuid.UUID
    created_at: datetime
    title: str = ""
    description: str = ""
    category: ProposalCategory = ProposalCategory.KNOWLEDGE_IMPROVEMENT
    state: ProposalState = ProposalState.GENERATED

    # Traceability chain (P-5)
    observation_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)

    # Content (P-2, P-9, P-10)
    rationale: str = ""
    intended_outcomes: tuple[str, ...] = field(default_factory=tuple)

    # Metadata
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty")

    @property
    def is_in_space(self) -> bool:
        return self.state == ProposalState.IN_SPACE