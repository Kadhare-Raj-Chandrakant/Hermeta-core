from dataclasses import dataclass
import uuid

from brain.evolution.transition_type import TransitionType


@dataclass(frozen=True)
class EvolutionOperation:
    target_id: uuid.UUID
    expected_version_id: uuid.UUID
    transition_type: TransitionType
    reason: str
