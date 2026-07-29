from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Observation:
    source_type: str
    content: str
    metadata: tuple[tuple[str, str], ...] = ()
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.source_type or not self.source_type.strip():
            raise ValueError("source_type must not be empty")
        if not self.content or not self.content.strip():
            raise ValueError("content must not be empty")
