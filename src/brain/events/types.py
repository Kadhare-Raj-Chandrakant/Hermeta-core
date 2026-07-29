from dataclasses import dataclass

from brain.events.event import Event


@dataclass(frozen=True)
class KnowledgeLearned(Event):
    knowledge_type: str = ""
    title: str = ""


@dataclass(frozen=True)
class ExecutionCompleted(Event):
    plan_id: str = ""
    actions_completed: int = 0


@dataclass(frozen=True)
class ExecutionFailed(Event):
    plan_id: str = ""
    error: str = ""


@dataclass(frozen=True)
class ReflectionCompleted(Event):
    findings_count: int = 0


@dataclass(frozen=True)
class ConflictDetected(Event):
    description: str = ""


@dataclass(frozen=True)
class PlanCompleted(Event):
    plan_id: str = ""
    confidence: float = 0.0
