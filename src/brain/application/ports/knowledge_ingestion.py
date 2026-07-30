from abc import ABC, abstractmethod

from brain.domain.version import KnowledgeVersion
from brain.pipeline.candidate import KnowledgeCandidate


class KnowledgeIngestionPort(ABC):
    @abstractmethod
    def learn(self, candidate: KnowledgeCandidate) -> KnowledgeVersion:
        """Persist a validated knowledge candidate and return the created version."""