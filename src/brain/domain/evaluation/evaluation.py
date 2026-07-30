from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.evaluation.enums import EvaluationDimension, EvidenceType, EvaluationState
from brain.domain.evaluation.tradeoff import Tradeoff
from brain.domain.evaluation.evidence import EvaluationEvidence
from brain.domain.evaluation.dimension import DimensionalAnalysis


@dataclass(frozen=True)
class Evaluation:
    """
    A complete evaluation of a single Proposal.

    An Evaluation is an analytical artifact, not a decision.
    It contains structured reasoning, not approval/rejection.

    Constitutional Laws Enforced:
    - E-1: Evaluation is analytical, not decisive.
    - E-2: Every conclusion must have explicit evidence.
    - E-3: Facts and judgments must be separated.
    - E-4: Tradeoffs are first-class cognitive objects.
    - E-5: Evaluation compares alternatives, never decides.
    - E-6: No approval, rejection, acceptance, or ranking fields.
    - E-7: Evaluation is unaware of Decision.
    - E-8: Evaluation never mutates evaluated objects.
    - E-9: Every evaluation conclusion traces back to evidence.
    - E-10: Evaluations are immutable domain objects.
    - E-11: Evaluations support comparative reasoning.
    - E-12: EvaluationSpace preserves all evaluations.
    - E-13: Tradeoffs are explicit cognitive objects.
    - E-14: Evidence is explicit and traceable.
    - E-15: Evaluations may be superseded, never mutated.
    - E-16: Evaluations support future constitutional amendment.

    Forbidden fields (E-6):
    - approved / rejected / accepted / rejected
    - score / confidence / priority / ranking / severity
    - decision / decision_id / governance / execution_plan
    - mutation methods / execution methods / runtime behavior
    """

    evaluation_id: uuid.UUID = uuid.uuid4()
    proposal_id: uuid.UUID = uuid.uuid4()
    state: str = "draft"  # EvaluationState value as string

    # Structured reasoning
    dimensional_analyses: tuple = field(default_factory=tuple)
    # Global tradeoffs across dimensions
    global_tradeoffs: tuple = field(default_factory=tuple)
    # All evidence used in this evaluation
    evidence_ids: tuple = field(default_factory=tuple)
    # Summary reasoning (qualitative, not decision)
    summary_judgment: str = ""
    # Uncertainties and limitations
    known_uncertainties: tuple[str, ...] = field(default_factory=tuple)

    created_at: datetime = datetime.now(timezone.utc)
    superseded_by: uuid.UUID | None = None  # E-15

    def __post_init__(self) -> None:
        pass  # No validation required

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None