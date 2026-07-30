from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.evaluation.enums import EvidenceType


@dataclass(frozen=True)
class EvaluationEvidence:
    """
    Explicit evidence supporting an evaluation conclusion.

    Evidence must remain explicit and traceable.
    Evaluation must never invent evidence.
    Evidence references existing cognitive objects without coupling.

    Evidence types:
    - OBSERVATION_BASED: Derived from self-observation signals
    - HYPOTHESIS_BASED: Derived from competing hypotheses
    - PROBLEM_BASED: Derived from problem formulation
    - PROPOSAL_BASED: Derived from proposal content
    - HISTORICAL_ANALOGY: Based on past evolution attempts
    - THEORETICAL_REASONING: Derived from architectural principles
    """

    evidence_id: uuid.UUID = uuid.uuid4()
    evidence_type: EvidenceType = EvidenceType.THEORETICAL_REASONING
    description: str = ""
    # Traceability references (immutable UUIDs)
    observation_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    hypothesis_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    problem_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    proposal_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    created_at: datetime = datetime.now(timezone.utc)
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")