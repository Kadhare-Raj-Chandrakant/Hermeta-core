from abc import ABC, abstractmethod

from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult


class ExecutionObserver(ABC):
    def on_started(self, record: ExecutionRecord) -> None:
        pass

    def on_completed(self, result: ExecutionResult) -> None:
        pass

    def on_failed(self, result: ExecutionResult) -> None:
        pass
