from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid

from brain.adapter.errors import AdapterNotReadyError


class AdapterLifecycleState(Enum):
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass(frozen=True)
class AdapterState:
    task_id: uuid.UUID
    state: AdapterLifecycleState
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AdapterLifecycle:
    def __init__(self) -> None:
        self._state: AdapterState | None = None

    def start(self, task_id: uuid.UUID) -> AdapterState:
        if self._state is not None and self._state.state == AdapterLifecycleState.ACTIVE:
            raise AdapterNotReadyError("Session already active")
        now = datetime.now(timezone.utc)
        self._state = AdapterState(
            task_id=task_id,
            state=AdapterLifecycleState.ACTIVE,
            started_at=now,
        )
        return self._state

    def complete(self) -> AdapterState:
        if self._state is None or self._state.state != AdapterLifecycleState.ACTIVE:
            raise AdapterNotReadyError("No active session to complete")
        now = datetime.now(timezone.utc)
        self._state = AdapterState(
            task_id=self._state.task_id,
            state=AdapterLifecycleState.COMPLETED,
            started_at=self._state.started_at,
            completed_at=now,
        )
        return self._state

    def check_active(self) -> None:
        if self._state is None or self._state.state != AdapterLifecycleState.ACTIVE:
            raise AdapterNotReadyError("No active session")

    @property
    def state(self) -> AdapterState | None:
        return self._state
