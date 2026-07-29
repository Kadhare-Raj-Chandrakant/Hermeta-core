from dataclasses import dataclass
import uuid

from brain.evolution.evolution_operation import EvolutionOperation


@dataclass(frozen=True)
class EvolutionPlan:
    operations: tuple[EvolutionOperation, ...]
    affected_targets: tuple[uuid.UUID, ...]
    metadata: tuple[tuple[str, str], ...] = ()
