import uuid
from datetime import datetime, timezone

import pytest

from brain.execution.context import ExecutionContext


class TestExecutionContextCreation:
    def test_create_minimal(self):
        ctx = ExecutionContext(plan_id=uuid.uuid4())
        assert isinstance(ctx.plan_id, uuid.UUID)
        assert ctx.project is None
        assert ctx.metadata == ()
        assert isinstance(ctx.started_at, datetime)

    def test_create_with_project(self):
        ctx = ExecutionContext(plan_id=uuid.uuid4(), project="myproject")
        assert ctx.project == "myproject"

    def test_create_with_metadata(self):
        meta = (("key1", "val1"), ("key2", "val2"))
        ctx = ExecutionContext(plan_id=uuid.uuid4(), metadata=meta)
        assert len(ctx.metadata) == 2
        assert ctx.metadata[0] == ("key1", "val1")


class TestExecutionContextImmutability:
    def test_frozen(self):
        ctx = ExecutionContext(plan_id=uuid.uuid4())
        with pytest.raises(AttributeError):
            ctx.project = "changed"

    def test_metadata_frozen(self):
        ctx = ExecutionContext(plan_id=uuid.uuid4())
        with pytest.raises(AttributeError):
            ctx.metadata = ()
