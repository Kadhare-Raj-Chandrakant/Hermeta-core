from dataclasses import dataclass
from datetime import datetime, timezone
import threading

from brain.application.brain_service import BrainService
from brain.application.usecases.models import KnowledgeVersionDTO
from brain.domain.task import Task
from brain.pipeline.candidate import KnowledgeCandidate
from brain.services.compiler import ContextPackage


@dataclass(frozen=True)
class SessionStatus:
    active: bool
    started_at: datetime | None
    task: Task | None
    learned_items: int


class BrainSession:
    def __init__(self, brain: BrainService) -> None:
        self._brain = brain
        self._task: Task | None = None
        self._started_at: datetime | None = None
        self._learned_items: int = 0
        self._lock = threading.RLock()

    def begin(self, task: Task) -> ContextPackage:
        with self._lock:
            if self._task is not None:
                raise RuntimeError("Session already active")
            self._task = task
            self._started_at = datetime.now(timezone.utc)
        return self._brain.prepare(task)

    def learn(self, candidate: KnowledgeCandidate) -> KnowledgeVersionDTO:
        with self._lock:
            if self._task is None:
                raise RuntimeError("No active session")
            self._learned_items += 1
        return self._brain.learn(candidate)

    def complete(self) -> None:
        with self._lock:
            if self._task is None:
                raise RuntimeError("No active session")
            self._task = None
            self._started_at = None
            self._learned_items = 0

    def status(self) -> SessionStatus:
        with self._lock:
            return SessionStatus(
                active=self._task is not None,
                started_at=self._started_at,
                task=self._task,
                learned_items=self._learned_items,
            )