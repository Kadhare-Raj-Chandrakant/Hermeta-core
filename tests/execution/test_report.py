import uuid
from datetime import datetime, timedelta, timezone

import pytest

from brain.execution.record import ExecutionRecord
from brain.execution.report import ExecutionReport
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus


def make_result(success: bool = True) -> ExecutionResult:
    record = ExecutionRecord(
        action_id=uuid.uuid4(),
        status=ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED,
        started_at=datetime.now(timezone.utc),
    )
    return ExecutionResult(
        record=record,
        success=success,
        output="ok" if success else "",
        error=None if success else "failed",
    )


class TestExecutionReportCreation:
    def test_create_valid(self):
        now = datetime.now(timezone.utc)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=now,
            completed_at=now,
        )
        assert isinstance(report.plan_id, uuid.UUID)
        assert report.results == ()
        assert report.started_at == now

    def test_with_results(self):
        now = datetime.now(timezone.utc)
        r1 = make_result(success=True)
        r2 = make_result(success=False)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(r1, r2),
            started_at=now,
            completed_at=now,
        )
        assert len(report.results) == 2


class TestExecutionReportProperties:
    def test_completed_count(self):
        results = (make_result(True), make_result(True), make_result(False))
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=results,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        assert report.completed == 2

    def test_failed_count(self):
        results = (make_result(True), make_result(False), make_result(False))
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=results,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        assert report.failed == 2

    def test_total_actions(self):
        results = (make_result(True), make_result(False), make_result(True))
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=results,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        assert report.total_actions == 3

    def test_empty_report(self):
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        assert report.completed == 0
        assert report.failed == 0
        assert report.total_actions == 0


class TestExecutionReportImmutability:
    def test_frozen(self):
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        with pytest.raises(AttributeError):
            report.results = ()
