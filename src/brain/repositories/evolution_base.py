from abc import ABC, abstractmethod
import uuid

from brain.evolution.conflict import Conflict
from brain.evolution.transition import KnowledgeTransition


class EvolutionRepository(ABC):
    @abstractmethod
    def create_transition(self, transition: KnowledgeTransition) -> None:
        """Store a KnowledgeTransition."""

    @abstractmethod
    def get_transitions_for_version(self, version_id: uuid.UUID) -> tuple[KnowledgeTransition, ...]:
        """Return all transitions where version_id appears as from or to."""

    @abstractmethod
    def get_all_transitions(self) -> tuple[KnowledgeTransition, ...]:
        """Return all stored transitions."""

    @abstractmethod
    def create_conflict(self, conflict: Conflict) -> None:
        """Store a Conflict."""

    @abstractmethod
    def get_conflicts(self) -> tuple[Conflict, ...]:
        """Return all stored conflicts."""

    @abstractmethod
    def save_execution_record(self, record: object) -> None:
        """Persist an execution record (EvolutionRecord or ExecutionFailureRecord)."""

    @abstractmethod
    def get_execution_records(self) -> tuple[object, ...]:
        """Return all stored execution records."""
