from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

from brain.domain.problem.enums import ProblemCategory, ProblemSeverity
from brain.domain.problem.hypothesis_space import HypothesisSpace


@dataclass(frozen=True)
class ProblemStatement:
    """
    A formally defined cognitive gap within Hermes.

    A ProblemStatement describes WHAT is wrong without prescribing HOW to fix it.
    It contains no solution, no recommendation, no implementation plan,
    and no proposal or evaluation references.
    """

    problem_id: uuid.UUID
    created_at: datetime
    title: str = ""
    description: str = ""
    category: ProblemCategory = ProblemCategory.OPERATIONAL
    severity: ProblemSeverity = ProblemSeverity.LOW
    observation_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    hypothesis_space_id: Optional[uuid.UUID] = None
    affected_targets: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not self.observation_ids:
            raise ValueError("observation_ids must not be empty")

    @property
    def has_hypothesis_space(self) -> bool:
        return self.hypothesis_space_id is not None

    @property
    def observation_count(self) -> int:
        return len(self.observation_ids)

    @property
    def affected_target_count(self) -> int:
        return len(self.affected_targets)