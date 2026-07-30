from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ProblemSpace:
    """
    A collection of related problems that share a common cognitive domain.

    A ProblemSpace groups related problems that may share hypotheses,
    observations, or cognitive domains. It provides a structured view
    of the problem landscape.
    """

    space_id: uuid.UUID = uuid.uuid4()
    problem_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        pass

    @property
    def problem_count(self) -> int:
        return len(self.problem_ids)

    @property
    def has_problems(self) -> bool:
        return len(self.problem_ids) > 0

    def with_problem(self, problem_id: uuid.UUID) -> "ProblemSpace":
        """Return a new ProblemSpace with the problem added (immutable)."""
        if problem_id in self.problem_ids:
            return self
        return ProblemSpace(
            space_id=uuid.uuid4(),
            problem_ids=self.problem_ids + (problem_id,),
            created_at=self.created_at,
        )