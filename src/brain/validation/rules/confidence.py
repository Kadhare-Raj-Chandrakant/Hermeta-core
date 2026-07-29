from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class ConfidenceRule(ValidationRule):
    def __init__(self, threshold: float = 0.3) -> None:
        self._threshold = threshold

    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        if candidate.confidence < self._threshold:
            return ValidationResult(
                passed=False,
                rule_name="ConfidenceRule",
                reason=f"Confidence {candidate.confidence} below threshold {self._threshold}",
            )
        return ValidationResult(
            passed=True,
            rule_name="ConfidenceRule",
            reason="Confidence accepted",
        )
