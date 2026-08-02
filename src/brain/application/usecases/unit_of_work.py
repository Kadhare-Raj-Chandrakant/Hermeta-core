from dataclasses import dataclass, field
import threading


@dataclass
class EvolutionUnitOfWork:
    _knowledge_repo: object = field(default=None, init=False)
    _evolution_repo: object = field(default=None, init=False)
    _knowledge_snapshot: object = field(default=None, init=False)
    _evolution_snapshot: object = field(default=None, init=False)
    _active: bool = field(default=False, init=False)
    _lock: object = field(default_factory=lambda: threading.RLock(), init=False, repr=False)

    def attach(self, knowledge, evolution) -> None:
        self._knowledge_repo = knowledge
        self._evolution_repo = evolution

    def begin(self) -> None:
        with self._lock:
            if self._active:
                raise RuntimeError("Transaction already active")
            repo = self._knowledge_repo
            if repo is not None and hasattr(repo, "snapshot"):
                self._knowledge_snapshot = repo.snapshot()
            repo = self._evolution_repo
            if repo is not None and hasattr(repo, "snapshot"):
                self._evolution_snapshot = repo.snapshot()
            self._active = True

    def commit(self) -> None:
        with self._lock:
            if not self._active:
                raise RuntimeError("No active transaction")
            self._knowledge_snapshot = None
            self._evolution_snapshot = None
            self._active = False

    def rollback(self) -> None:
        with self._lock:
            if not self._active:
                raise RuntimeError("No active transaction")
            repo = self._knowledge_repo
            if self._knowledge_snapshot is not None and repo is not None and hasattr(repo, "restore"):
                repo.restore(self._knowledge_snapshot)
            repo = self._evolution_repo
            if self._evolution_snapshot is not None and repo is not None and hasattr(repo, "restore"):
                repo.restore(self._evolution_snapshot)
            self._knowledge_snapshot = None
            self._evolution_snapshot = None
            self._active = False
