import uuid
from datetime import datetime, timezone

import pytest

from brain.execution.record import ExecutionRecord
from brain.execution.status import ExecutionStatus


class TestExecutionRecordCreation:
    def test_create_valid(self):
        now = datetime.now(timezone.utc)
        r = ExecutionRecord(
            action_id=uuid.uuid4(),
            status=ExecutionStatus.RUNNING,
            started_at=now,
        )
        assert isinstance(r.id, uuid.UUID)
        assert isinstance(r.action_id, uuid.UUID)
        assert r.status == ExecutionStatus.RUNNING
        assert r.started_at == now
        assert r.completed_at is None

    def test_create_with_completed_at(self):
        now = datetime.now(timezone.utc)
        later = datetime.now(timezone.utc)
        r = ExecutionRecord(
            action_id=uuid.uuid4(),
            status=ExecutionStatus.COMPLETED,
            started_at=now,
            completed_at=later,
        )
        assert r.completed_at == later


class TestExecutionRecordValidation:
    def test_completed_at_before_started_at_raises(self):
        now = datetime.now(timezone.utc)
        before = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="completed_at cannot be before started_at"):
            ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.FAILED,
                started_at=now,
                completed_at=before,
            )


class TestExecutionRecordImmutability:
    def test_frozen(self):
        r = ExecutionRecord(
            action_id=uuid.uuid4(),
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        with pytest.raises(AttributeError):
            r.status = ExecutionStatus.FAILED
