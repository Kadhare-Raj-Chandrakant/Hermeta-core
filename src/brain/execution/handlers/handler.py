from abc import ABC, abstractmethod

from brain.execution.context import ExecutionContext
from brain.execution.result import ExecutionResult
from brain.planning.action import Action


class ActionHandler(ABC):
    @abstractmethod
    def can_handle(self, action: Action) -> bool:
        ...

    @abstractmethod
    def execute(
        self,
        action: Action,
        context: ExecutionContext,
    ) -> ExecutionResult:
        ...
