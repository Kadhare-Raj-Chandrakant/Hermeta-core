from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class KnowledgeIdentity:
    id: uuid.UUID
    created_at: datetime

    @classmethod
    def create(cls) -> "KnowledgeIdentity":
        return cls(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
        )
