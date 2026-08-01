from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.evaluation.enums import EvaluationDimension, EvidenceType
from brain.domain.evaluation.evidence import EvaluationEvidence


@dataclass(frozen=True)
class DimensionalAnalysis:
    """
    Analysis of a proposal along a single evaluation dimension.

    A dimensional analysis is NOT a score.
    It is structured reasoning about how the proposal relates to one dimension.
    """

    analysis_id: uuid.UUID
    created_at: datetime
    dimension: EvaluationDimension = EvaluationDimension.ARCHITECTURAL_INTEGRITY
    # Facts: objective statements about the proposal
    facts: tuple[str, ...] = field(default_factory=tuple)
    # Judgments: reasoned interpretations
    judgments: tuple[str, ...] = field(default_factory=tuple)
    # Supporting evidence for this dimension
    evidence: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    # Tradeoffs specific to this dimension
    tradeoff_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        pass  # No validation required - empty is valid