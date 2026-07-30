from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from brain.domain.evolution.intent import EvolutionIntent
from brain.domain.evolution.policy import EvolutionPolicy


@dataclass(frozen=True)
class EvolutionPlan:
    plan_id: uuid.UUID
    trigger_id: uuid.UUID
    intents: tuple[EvolutionIntent, ...]
    policy: EvolutionPolicy
    created_at: datetime
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.intents:
            raise ValueError("plan must contain at least one intent")
        if self.created_at is None:
            raise ValueError("created_at must be set")

    @property
    def operation_count(self) -> int:
        return len(self.intents)

    @property
    def affected_identities(self) -> tuple[uuid.UUID, ...]:
        return tuple(sorted({intent.target_identity for intent in self.intents}))