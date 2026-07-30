from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

from brain.domain.problem.enums import HypothesisCategory


@dataclass(frozen=True)
class Hypothesis:
    """
    One possible explanation for observations.

    A Hypothesis represents a candidate explanation — not a solution.
    It never recommends action, never contains execution information,
    and never includes governance or approval.

    Multiple hypotheses may exist for the same observations (H-2).
    """

    hypothesis_id: uuid.UUID = uuid.uuid4()
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    supporting_observation_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    category: HypothesisCategory = HypothesisCategory.CAUSAL
    hypothesis_space_id: Optional[uuid.UUID] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.supporting_observation_ids:
            raise ValueError("supporting_observation_ids must not be empty")

    @property
    def has_hypothesis_space(self) -> bool:
        return self.hypothesis_space_id is not None