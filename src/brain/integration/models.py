import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class IntegrationSection:
    section_type: str
    title: str
    content: tuple[str, ...]


@dataclass(frozen=True)
class IntegrationTask:
    task_id: uuid.UUID
    objective: str
    project: str
    component: str
    task_type: str
    metadata: tuple[tuple[str, str], ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective must not be empty")
        if not self.project.strip():
            raise ValueError("project must not be empty")
        if not self.component.strip():
            raise ValueError("component must not be empty")


@dataclass(frozen=True)
class IntegrationContext:
    task_id: uuid.UUID
    sections: tuple[IntegrationSection, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class IntegrationLearning:
    task_id: uuid.UUID
    knowledge_type: str
    title: str
    understanding: str
    confidence: float
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
