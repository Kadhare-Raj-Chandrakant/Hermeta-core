import uuid
from datetime import datetime, timedelta, timezone

import pytest

from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus


def make_record(**kwargs) -> ExecutionRecord:
    defaults = dict(
        action_id=uuid.uuid4(),
        status=ExecutionStatus.COMPLETED,
        started_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return ExecutionRecord(**defaults)


class TestExecutionResultCreation:
    def test_create_success(self):
        record = make_record()
        r = ExecutionResult(
            record=record,
            success=True,
            output="All tests passed",
        )
        assert r.record is record
        assert r.success is True
        assert r.output == "All tests passed"
        assert r.error is None
        assert r.duration == timedelta(0)

    def test_create_failure(self):
        record = make_record(status=ExecutionStatus.FAILED)
        r = ExecutionResult(
            record=record,
            success=False,
            output="",
            error="Test failed",
            duration=timedelta(seconds=5),
        )
        assert r.success is False
        assert r.error == "Test failed"
        assert r.duration == timedelta(seconds=5)


class TestExecutionResultImmutability:
    def test_frozen(self):
        record = make_record()
        r = ExecutionResult(record=record, success=True, output="ok")
        with pytest.raises(AttributeError):
            r.success = False

    def test_output_frozen(self):
        record = make_record()
        r = ExecutionResult(record=record, success=True, output="ok")
        with pytest.raises(AttributeError):
            r.output = "changed"
