from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    rule_name: str
    reason: str
