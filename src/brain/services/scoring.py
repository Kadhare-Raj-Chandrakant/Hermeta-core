from abc import ABC, abstractmethod

from brain.domain.version import KnowledgeVersion


class ScoringFactor(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this factor."""

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight of this factor in the final score."""

    @abstractmethod
    def score(self, intent: str, version: KnowledgeVersion) -> float:
        """Return a score between 0.0 and 1.0 for this version given the intent."""
