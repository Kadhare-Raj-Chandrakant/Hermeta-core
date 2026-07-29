import uuid
from dataclasses import dataclass

from brain.domain.enums import KnowledgeType


@dataclass(frozen=True)
class PlanningContext:
    task_id: uuid.UUID | None = None
    knowledge_types: tuple[KnowledgeType, ...] = ()
    constraints: tuple[str, ...] = ()
