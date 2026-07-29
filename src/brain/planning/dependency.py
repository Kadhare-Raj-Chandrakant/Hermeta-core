import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Dependency:
    from_action_id: uuid.UUID
    to_action_id: uuid.UUID
    reason: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if self.from_action_id == self.to_action_id:
            raise ValueError("from_action_id cannot equal to_action_id")
        if not self.reason or not self.reason.strip():
            raise ValueError("reason must not be empty")
