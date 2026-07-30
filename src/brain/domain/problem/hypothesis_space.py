from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

from brain.domain.problem.hypothesis import Hypothesis


@dataclass(frozen=True)
class HypothesisSpace:
    """
    A collection of competing hypotheses for the same observations.

    The space is a passive container — it does not rank, evaluate,
    filter, or choose between hypotheses. It preserves traceability
    from observations through hypotheses.
    """

    space_id: uuid.UUID = uuid.uuid4()
    observation_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    hypotheses: tuple[Hypothesis, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.observation_ids:
            raise ValueError("observation_ids must not be empty")

    @property
    def hypothesis_count(self) -> int:
        return len(self.hypotheses)

    @property
    def has_hypotheses(self) -> bool:
        return len(self.hypotheses) > 0