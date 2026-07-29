from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class EvolutionContext:
    previous_failures: tuple[tuple[uuid.UUID, ...], ...] = ()
    attempt_count: int = 0
    quarantined_targets: tuple[uuid.UUID, ...] = ()
    planning_policy: str = "default"
