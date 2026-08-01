from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.domain.observation.observation import SystemObservation


@dataclass(frozen=True)
class ObservationSnapshot:
    """
    Hermes observed state at a point in time.

    A snapshot is a collection of observations taken together.
    It represents the "what is" at a specific moment.

    Does NOT:
    - Compare with other snapshots
    - Calculate trends
    - Detect improvements or regressions
    - Generate proposals
    """

    snapshot_id: uuid.UUID
    timestamp: datetime
    collection_id: uuid.UUID
    observations: tuple[SystemObservation, ...] = ()

    def __post_init__(self) -> None:
        if not self.observations:
            raise ValueError("snapshot must contain at least one observation")

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    def observations_by_category(self) -> dict[str, tuple[SystemObservation, ...]]:
        """Group observations by category."""
        result: dict[str, list[SystemObservation]] = {}
        for obs in self.observations:
            cat = obs.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(obs)
        return {k: tuple(v) for k, v in result.items()}

    def observations_by_target(self) -> dict[str, tuple[SystemObservation, ...]]:
        """Group observations by target."""
        result: dict[str, list[SystemObservation]] = {}
        for obs in self.observations:
            if obs.target not in result:
                result[obs.target] = []
            result[obs.target].append(obs)
        return {k: tuple(v) for k, v in result.items()}