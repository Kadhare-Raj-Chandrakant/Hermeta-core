from brain.execution.errors import NoHandlerError
from brain.execution.handlers.handler import ActionHandler
from brain.planning.action import Action


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: list[ActionHandler] = []

    def register(self, handler: ActionHandler) -> None:
        self._handlers.append(handler)

    def find(self, action: Action) -> ActionHandler:
        for handler in self._handlers:
            if handler.can_handle(action):
                return handler
        raise NoHandlerError(f"No handler found for action: {action.title}")

    @property
    def handlers(self) -> tuple[ActionHandler, ...]:
        return tuple(self._handlers)
