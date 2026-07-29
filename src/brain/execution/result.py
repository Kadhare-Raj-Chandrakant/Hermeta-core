from dataclasses import dataclass
from datetime import timedelta

from brain.execution.record import ExecutionRecord


@dataclass(frozen=True)
class ExecutionResult:
    record: ExecutionRecord
    success: bool
    output: str
    error: str | None = None
    duration: timedelta = timedelta(0)
