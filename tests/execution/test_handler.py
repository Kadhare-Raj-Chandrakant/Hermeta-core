import uuid

import pytest

from brain.execution.context import ExecutionContext
from brain.execution.handlers.handler import ActionHandler
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.planning.action import Action
from datetime import datetime, timezone


class StubHandler(ActionHandler):
    def __init__(self, can: bool = True) -> None:
        self._can = can

    def can_handle(self, action: Action) -> bool:
        return self._can

    def execute(self, action: Action, context: ExecutionContext) -> ExecutionResult:
        from brain.execution.record import ExecutionRecord
        record = ExecutionRecord(
            action_id=action.id,
            status=ExecutionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc),
        )
        return ExecutionResult(record=record, success=True, output="stub")


class TestHandlerRegistryCreation:
    def test_create_empty(self):
        reg = HandlerRegistry()
        assert len(reg.handlers) == 0


class TestHandlerRegistryRegister:
    def test_register_one(self):
        reg = HandlerRegistry()
        h = StubHandler()
        reg.register(h)
        assert len(reg.handlers) == 1

    def test_register_multiple(self):
        reg = HandlerRegistry()
        reg.register(StubHandler())
        reg.register(StubHandler(can=False))
        assert len(reg.handlers) == 2


class TestHandlerRegistryFind:
    def test_find_matching(self):
        reg = HandlerRegistry()
        h = StubHandler(can=True)
        reg.register(h)
        action = Action(goal_id=uuid.uuid4(), title="Test", description="desc")
        found = reg.find(action)
        assert found is h

    def test_find_first_match(self):
        reg = HandlerRegistry()
        h1 = StubHandler(can=True)
        h2 = StubHandler(can=True)
        reg.register(h1)
        reg.register(h2)
        action = Action(goal_id=uuid.uuid4(), title="Test", description="desc")
        found = reg.find(action)
        assert found is h1

    def test_missing_handler_raises(self):
        reg = HandlerRegistry()
        reg.register(StubHandler(can=False))
        action = Action(goal_id=uuid.uuid4(), title="Test", description="desc")
        with pytest.raises(Exception):
            reg.find(action)

    def test_empty_registry_raises(self):
        reg = HandlerRegistry()
        action = Action(goal_id=uuid.uuid4(), title="Test", description="desc")
        with pytest.raises(Exception):
            reg.find(action)
