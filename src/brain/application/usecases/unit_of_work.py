from dataclasses import dataclass, field


@dataclass
class EvolutionUnitOfWork:
    _knowledge_repo: object = field(default=None, init=False)
    _evolution_repo: object = field(default=None, init=False)
    _knowledge_snapshot: object = field(default=None, init=False)
    _evolution_snapshot: object = field(default=None, init=False)
    _active: bool = field(default=False, init=False)

    def attach(self, knowledge, evolution) -> None:
        self._knowledge_repo = knowledge
        self._evolution_repo = evolution

    def begin(self) -> None:
        if self._active:
            raise RuntimeError("Transaction already active")
        if hasattr(self._knowledge_repo, "snapshot"):
            self._knowledge_snapshot = self._knowledge_repo.snapshot()
        if hasattr(self._evolution_repo, "snapshot"):
            self._evolution_snapshot = self._evolution_repo.snapshot()
        self._active = True

    def commit(self) -> None:
        if not self._active:
            raise RuntimeError("No active transaction")
        self._knowledge_snapshot = None
        self._evolution_snapshot = None
        self._active = False

    def rollback(self) -> None:
        if not self._active:
            raise RuntimeError("No active transaction")
        if self._knowledge_snapshot is not None and hasattr(self._knowledge_repo, "restore"):
            self._knowledge_repo.restore(self._knowledge_snapshot)
        if self._evolution_snapshot is not None and hasattr(self._evolution_repo, "restore"):
            self._evolution_repo.restore(self._evolution_snapshot)
        self._knowledge_snapshot = None
        self._evolution_snapshot = None
        self._active = False
