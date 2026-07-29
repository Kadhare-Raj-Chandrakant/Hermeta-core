from abc import ABC, abstractmethod

from brain.detection.observation import Observation
from brain.pipeline.candidate import KnowledgeCandidate


class KnowledgeDetector(ABC):
    @abstractmethod
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        ...
