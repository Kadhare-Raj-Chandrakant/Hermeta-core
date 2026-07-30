from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.evaluation.evaluation import Evaluation


@dataclass(frozen=True)
class EvaluationSpace:
    """
    A complete set of evaluations for one or more proposals.

    An EvaluationSpace preserves ALL evaluations for a problem space.
    It never ranks, filters, selects, or discards evaluations.

    Constitutional Laws Enforced:
    - E-12: EvaluationSpace preserves all evaluations for comparative reasoning.
    - E-12: EvaluationSpace never ranks, filters, selects, or discards.
    - E-12: EvaluationSpace supports comparative reasoning.
    """

    space_id: uuid.UUID = uuid.uuid4()
    problem_statement_id: uuid.UUID = uuid.uuid4()
    proposal_ids: tuple = field(default_factory=tuple)
    evaluations: tuple = field(default_factory=tuple)
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        pass

    @property
    def evaluation_count(self) -> int:
        return len(self.evaluations)

    @property
    def proposal_count(self) -> int:
        return len(self.proposal_ids)

    def evaluations_by_proposal(self) -> dict:
        """Group evaluations by proposal for deterministic access."""
        result: dict = {}
        for eval in self.evaluations:
            pid = str(eval.proposal_id)
            if pid not in result:
                result[pid] = []
            result[pid].append(eval)
        return {k: tuple(v) for k, v in result.items()}

    def get_latest_evaluation(self, proposal_id: uuid.UUID) -> Evaluation | None:
        """Get the latest (non-superseded) evaluation for a proposal."""
        for eval in self.evaluations:
            if eval.proposal_id == proposal_id and not eval.is_superseded:
                return eval
        return None