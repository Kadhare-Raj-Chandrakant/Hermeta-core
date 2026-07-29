import pytest

from brain.execution.status import ExecutionStatus


class TestExecutionStatusValues:
    def test_pending(self):
        assert ExecutionStatus.PENDING.value == "pending"

    def test_running(self):
        assert ExecutionStatus.RUNNING.value == "running"

    def test_completed(self):
        assert ExecutionStatus.COMPLETED.value == "completed"

    def test_failed(self):
        assert ExecutionStatus.FAILED.value == "failed"

    def test_cancelled(self):
        assert ExecutionStatus.CANCELLED.value == "cancelled"

    def test_blocked(self):
        assert ExecutionStatus.BLOCKED.value == "blocked"

    def test_six_values(self):
        assert len(ExecutionStatus) == 6


class TestExecutionStatusImmutability:
    def test_is_enum(self):
        assert ExecutionStatus.PENDING is ExecutionStatus.PENDING

    def test_members_are_hashable(self):
        assert hash(ExecutionStatus.RUNNING) == hash(ExecutionStatus.RUNNING)
