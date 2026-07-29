from dataclasses import dataclass

from brain.validation.result import ValidationResult


@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    results: tuple[ValidationResult, ...]
