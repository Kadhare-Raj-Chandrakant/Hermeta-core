from abc import ABC, abstractmethod

from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.result import ValidationResult


class ValidationRule(ABC):
    @abstractmethod
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        ...
