import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from brain.execution.result import ExecutionResult


@dataclass(frozen=True)
class ExecutionReport:
    plan_id: uuid.UUID
    results: tuple[ExecutionResult, ...]
    started_at: datetime
    completed_at: datetime

    @property
    def completed(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def total_actions(self) -> int:
        return len(self.results)
