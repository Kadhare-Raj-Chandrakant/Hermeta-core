from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.proposal.proposal import Proposal


@dataclass(frozen=True)
class ProposalSpace:
    """
    The complete set of candidate proposals for a ProblemStatement.

    A ProposalSpace is a CONTAINER that preserves alternatives.
    It does NOT rank, filter, merge, or optimize proposals.

    Constitutional Laws Enforced:
    - P-7: ProposalSpace owns alternatives. Multiple proposals coexist.
    - P-7: ProposalSpace never ranks, removes, filters, merges, or optimizes.
    - P-7: Proposal generation is creative; evaluation is analytical.
    - P-8: ProposalSpace is unaware of Evaluation/Decision/Execution.
    """

    space_id: uuid.UUID = uuid.uuid4()
    problem_statement_id: uuid.UUID = uuid.uuid4()
    proposals: tuple[Proposal, ...] = field(default_factory=tuple)
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if self.problem_statement_id is None:
            raise ValueError("problem_statement_id must not be None")

    @property
    def proposal_count(self) -> int:
        return len(self.proposals)

    @property
    def has_proposals(self) -> bool:
        return len(self.proposals) > 0

    def proposals_by_category(self) -> dict[str, tuple[Proposal, ...]]:
        """Group proposals by category for deterministic ordering."""
        result: dict[str, list[Proposal]] = {}
        for p in self.proposals:
            cat = p.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(p)
        return {k: tuple(v) for k, v in result.items()}