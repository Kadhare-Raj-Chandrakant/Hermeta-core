import uuid
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from brain.domain.task import TaskType


class FindingType(Enum):
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
    OBSOLETE = "obsolete"
    GAP = "gap"


@dataclass(frozen=True)
class ReflectionFindingDTO:
    finding_type: FindingType
    affected_versions: tuple[uuid.UUID, ...]
    explanation: str
    confidence: float


@dataclass(frozen=True)
class PlanningRequest:
    task_type: TaskType
    project: str
    component: str
    objective: str
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PlanningSummary:
    plan_id: uuid.UUID
    plan_status: str
    goal_count: int
    action_count: int
    dependency_count: int
    blocker_count: int


@dataclass(frozen=True)
class PlanningSummary:
    plan_id: uuid.UUID
    plan_status: str
    goal_count: int
    action_count: int
    dependency_count: int
    blocker_count: int


@dataclass(frozen=True)
class PlanDTO:
    plan_id: uuid.UUID
    plan_status: str
    goal_title: str
    goal_description: str
    project: str
    action_count: int
    dependency_count: int
    blocker_count: int


@dataclass(frozen=True)
class ExecutionRequest:
    plan_id: uuid.UUID
    project: str = ""
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ExecutionSummary:
    execution_started: bool
    execution_completed: bool
    execution_success: bool
    executed_action_count: int
    failed_action_count: int
    cancelled_action_count: int
    execution_duration: timedelta


@dataclass(frozen=True)
class LearningRequest:
    execution_success: bool
    executed_count: int
    failed_count: int
    cancelled_count: int
    duration: timedelta
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class LearningSummary:
    learning_started: bool
    learning_completed: bool
    learning_success: bool
    observations_created: int
    knowledge_updated: int
    learning_duration: timedelta


@dataclass(frozen=True)
class ReflectionRequest:
    scope: str
    project: str = ""
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReflectionSummary:
    reflection_started: bool
    reflection_completed: bool
    reflection_success: bool
    reflection_duration: timedelta
    finding_count: int
    duplicate_count: int
    conflict_count: int
    obsolete_count: int
    gap_count: int


@dataclass(frozen=True)
class EvolutionRequest:
    targets: tuple[uuid.UUID, ...] = ()
    context: str = ""
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class EvolutionContextDTO:
    attempt_counts: tuple[tuple[uuid.UUID, int], ...] = ()
    quarantined_targets: tuple[uuid.UUID, ...] = ()


@dataclass(frozen=True)
class PlanningMetrics:
    """Planning statistics — coexists with ExecutionMetrics."""
    planned_operations_count: int = 0
    affected_targets_count: int = 0
    quarantined_skipped: int = 0


@dataclass(frozen=True)
class ExecutionMetrics:
    """Execution statistics — coexists with PlanningMetrics."""
    executed_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    rolled_back: bool = False
    optimistic_conflicts: int = 0
    transaction_duration: timedelta = timedelta(0)


@dataclass(frozen=True)
class EvolutionSummary:
    evolution_started: bool
    evolution_completed: bool
    evolution_success: bool
    evolution_duration: timedelta
    planning: PlanningMetrics = PlanningMetrics()
    execution: ExecutionMetrics = ExecutionMetrics()


@dataclass(frozen=True)
class KnowledgeVersionDTO:
    version_id: uuid.UUID
    identity_id: uuid.UUID
    version_number: int
    knowledge_type: str
    title: str
    understanding: str
    confidence: float
    lifecycle_state: str
    created_at: str
