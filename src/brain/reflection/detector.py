from abc import ABC, abstractmethod

from brain.domain.version import KnowledgeVersion
from brain.reflection.finding import ReflectionFinding


class ReflectionDetector(ABC):
    @abstractmethod
    def analyze(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> tuple[ReflectionFinding, ...]:
        ...
