from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.report import ValidationReport
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class ValidationEngine:
    def __init__(self, rules: tuple[ValidationRule, ...]) -> None:
        self._rules = rules

    def validate(self, candidate: KnowledgeCandidate) -> ValidationReport:
        results: list[ValidationResult] = []
        for rule in self._rules:
            result = rule.validate(candidate)
            results.append(result)

        passed = all(r.passed for r in results)

        return ValidationReport(passed=passed, results=tuple(results))
