from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class Evidence:
    source: str
    reference: str


@dataclass(frozen=True)
class Relationship:
    target_id: uuid.UUID
    relationship_type: str
