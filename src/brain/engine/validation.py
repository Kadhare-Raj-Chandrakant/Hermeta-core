# Validation Utilities

"""
Shared validation utilities for all Hermes engines.
"""

from typing import Any, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from enum import Enum


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    severity: ValidationSeverity = ValidationSeverity.ERROR
    message: str = ""
    field: str = ""
    code: str = ""
    
    @staticmethod
    def ok() -> 'ValidationResult':
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def error(message: str, field: str = "", code: str = "") -> 'ValidationResult':
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=message,
            field=field,
            code=code
        )
    
    @staticmethod
    def warning(message: str, field: str = "", code: str = "") -> 'ValidationResult':
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            message=message,
            field=field,
            code=code
        )


@dataclass(frozen=True)
class ValidationReport:
    """Complete validation report."""
    results: Tuple[ValidationResult, ...] = ()
    
    @property
    def is_valid(self) -> bool:
        return all(r.is_valid for r in self.results)
    
    @property
    def errors(self) -> Tuple[ValidationResult, ...]:
        return tuple(r for r in self.results if r.severity == ValidationSeverity.ERROR)
    
    @property
    def warnings(self) -> Tuple[ValidationResult, ...]:
        return tuple(r for r in self.results if r.severity == ValidationSeverity.WARNING)
    
    def add(self, result: ValidationResult) -> 'ValidationReport':
        return ValidationReport(results=self.results + (result,))
    
    def merge(self, other: 'ValidationReport') -> 'ValidationReport':
        return ValidationReport(results=self.results + other.results)


class Validator:
    """Fluent validation builder."""
    
    def __init__(self, value: Any, field_name: str = ""):
        self._value = value
        self._field_name = field_name
        self._results: List[ValidationResult] = []
    
    def required(self, message: str = "") -> 'Validator':
        """Value must not be None or empty."""
        if self._value is None:
            self._results.append(ValidationResult.error(
                message or f"{self._field_name} is required",
                field=self._field_name,
                code="REQUIRED"
            ))
        elif isinstance(self._value, str) and not self._value.strip():
            self._results.append(ValidationResult.error(
                message or f"{self._field_name} cannot be empty",
                field=self._field_name,
                code="EMPTY"
            ))
        elif isinstance(self._value, (list, tuple)) and not self._value:
            self._results.append(ValidationResult.error(
                message or f"{self._field_name} cannot be empty",
                field=self._field_name,
                code="EMPTY"
            ))
        return self
    
    def uuid(self, message: str = "") -> 'Validator':
        """Value must be a valid UUID."""
        if self._value is not None:
            if isinstance(self._value, UUID):
                pass  # Valid UUID object
            elif isinstance(self._value, str):
                try:
                    UUID(self._value)
                except ValueError:
                    self._results.append(ValidationResult.error(
                        message or f"{self._field_name} must be a valid UUID",
                        field=self._field_name,
                        code="INVALID_UUID"
                    ))
            else:
                self._results.append(ValidationResult.error(
                    message or f"{self._field_name} must be a UUID",
                    field=self._field_name,
                    code="INVALID_UUID"
                ))
        return self
    
    def min_length(self, min_len: int, message: str = "") -> 'Validator':
        """String must have minimum length."""
        if self._value is not None and isinstance(self._value, str):
            if len(self._value) < min_len:
                self._results.append(ValidationResult.error(
                    message or f"{self._field_name} must be at least {min_len} characters",
                    field=self._field_name,
                    code="MIN_LENGTH"
                ))
        return self
    
    def max_length(self, max_len: int, message: str = "") -> 'Validator':
        """String must not exceed maximum length."""
        if self._value is not None and isinstance(self._value, str):
            if len(self._value) > max_len:
                self._results.append(ValidationResult.error(
                    message or f"{self._field_name} must not exceed {max_len} characters",
                    field=self._field_name,
                    code="MAX_LENGTH"
                ))
        return self
    
    def in_range(self, min_val: float, max_val: float, message: str = "") -> 'Validator':
        """Numeric value must be in range."""
        if self._value is not None:
            try:
                val = float(self._value)
                if val < min_val or val > max_val:
                    self._results.append(ValidationResult.error(
                        message or f"{self._field_name} must be between {min_val} and {max_val}",
                        field=self._field_name,
                        code="OUT_OF_RANGE"
                    ))
            except (ValueError, TypeError):
                self._results.append(ValidationResult.error(
                    message or f"{self._field_name} must be a number",
                    field=self._field_name,
                    code="NOT_A_NUMBER"
                ))
        return self
    
    def one_of(self, allowed: Tuple[Any, ...], message: str = "") -> 'Validator':
        """Value must be one of allowed values."""
        if self._value is not None and self._value not in allowed:
            self._results.append(ValidationResult.error(
                message or f"{self._field_name} must be one of {allowed}",
                field=self._field_name,
                code="INVALID_CHOICE"
            ))
        return self
    
    def matches(self, pattern: str, message: str = "") -> 'Validator':
        """String must match regex pattern."""
        import re
        if self._value is not None and isinstance(self._value, str):
            if not re.match(pattern, self._value):
                self._results.append(ValidationResult.error(
                    message or f"{self._field_name} does not match required pattern",
                    field=self._field_name,
                    code="PATTERN_MISMATCH"
                ))
        return self
    
    def custom(self, check: Callable[[Any], bool], message: str = "", code: str = "CUSTOM") -> 'Validator':
        """Custom validation function."""
        if self._value is not None and not check(self._value):
            self._results.append(ValidationResult.error(
                message or f"{self._field_name} failed custom validation",
                field=self._field_name,
                code=code
            ))
        return self
    
    def each(self, validator_fn: Callable[['Validator'], 'Validator']) -> 'Validator':
        """Apply validator to each item in a sequence."""
        if self._value is not None and isinstance(self._value, (list, tuple)):
            for i, item in enumerate(self._value):
                child_validator = Validator(item, f"{self._field_name}[{i}]")
                validator_fn(child_validator)
                self._results.extend(child_validator._results)
        return self
    
    def build(self) -> ValidationReport:
        """Build the validation report."""
        return ValidationReport(results=tuple(self._results))


def validate(value: Any, field_name: str = "") -> Validator:
    """Create a validator for a value."""
    return Validator(value, field_name)


# Common validation patterns
def validate_uuid(value: Any, field_name: str = "id") -> UUID:
    """Validate and return UUID."""
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid UUID")
    raise ValueError(f"{field_name} must be a UUID or valid UUID string")


def validate_positive_int(value: Any, field_name: str = "value") -> int:
    """Validate positive integer."""
    if isinstance(value, int) and value > 0:
        return value
    try:
        val = int(value)
        if val > 0:
            return val
    except (ValueError, TypeError):
        pass
    raise ValueError(f"{field_name} must be a positive integer")


def validate_non_empty_string(value: Any, field_name: str = "value") -> str:
    """Validate non-empty string."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"{field_name} must be a non-empty string")


def validate_enum_value(value: Any, enum_class: type, field_name: str = "value") -> Enum:
    """Validate enum value."""
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str):
        try:
            return enum_class(value)
        except ValueError:
            pass
    raise ValueError(f"{field_name} must be a valid {enum_class.__name__}")


def validate_uuid_sequence(values: Any, field_name: str = "ids") -> Tuple[UUID, ...]:
    """Validate sequence of UUIDs."""
    if isinstance(values, (list, tuple)):
        result = []
        for i, v in enumerate(values):
            result.append(validate_uuid(v, f"{field_name}[{i}]"))
        return tuple(result)
    raise ValueError(f"{field_name} must be a sequence of UUIDs")


def validate_non_empty_tuple(values: Any, field_name: str = "values") -> Tuple[Any, ...]:
    """Validate non-empty tuple."""
    if isinstance(values, tuple) and len(values) > 0:
        return values
    if isinstance(values, list) and len(values) > 0:
        return tuple(values)
    raise ValueError(f"{field_name} must be a non-empty tuple")