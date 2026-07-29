import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from brain.adapter.models import AdapterTask


@dataclass(frozen=True)
class WorkflowReport:
    session_id: uuid.UUID
    started_at: datetime
    completed_at: datetime
    duration: timedelta
    success: bool
    failure_reason: str | None
    task: AdapterTask
    context_available: bool
    plan_generated: bool
    execution_performed: bool
    learning_performed: bool
    reflection_performed: bool
    evolution_performed: bool
    plan_available: bool
    plan_status: str
    goal_count: int
    action_count: int
    dependency_count: int
    blocker_count: int
    planning_duration: timedelta
    execution_started: bool
    execution_completed: bool
    execution_success: bool
    executed_action_count: int
    failed_action_count: int
    cancelled_action_count: int
    execution_duration: timedelta
    learning_started: bool
    learning_completed: bool
    learning_success: bool
    observations_created: int
    knowledge_updated: int
    learning_duration: timedelta
