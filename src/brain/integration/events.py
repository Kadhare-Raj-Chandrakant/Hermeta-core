import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Union


@dataclass(frozen=True)
class TaskStarted:
    task_id: uuid.UUID
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ContextPrepared:
    task_id: uuid.UUID
    section_count: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class KnowledgeLearned:
    task_id: uuid.UUID
    knowledge_type: str
    title: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TaskCompleted:
    task_id: uuid.UUID
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class LearningFailed:
    task_id: uuid.UUID
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("reason must not be empty")


@dataclass(frozen=True)
class ContextUnavailable:
    task_id: uuid.UUID
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("reason must not be empty")


IntegrationEvent = Union[
    TaskStarted,
    ContextPrepared,
    KnowledgeLearned,
    TaskCompleted,
    LearningFailed,
    ContextUnavailable,
]
