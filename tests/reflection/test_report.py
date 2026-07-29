from datetime import timedelta

import pytest

from brain.reflection.report import ReflectionReport
from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType
import uuid


def make_finding(**kwargs) -> ReflectionFinding:
    defaults = dict(
        reflection_type=ReflectionType.DUPLICATE,
        affected_versions=(uuid.uuid4(),),
        explanation="Test finding",
        confidence=0.8,
    )
    defaults.update(kwargs)
    return ReflectionFinding(**defaults)


def make_report(**kwargs) -> ReflectionReport:
    defaults = dict(
        versions_checked=5,
        detectors_used=("DuplicateDetector",),
        findings=(make_finding(),),
        duration=timedelta(seconds=1.0),
    )
    defaults.update(kwargs)
    return ReflectionReport(**defaults)


class TestReflectionReportCreation:
    def test_create_valid(self):
        r = make_report()
        assert r.versions_checked == 5
        assert r.detectors_used == ("DuplicateDetector",)
        assert len(r.findings) == 1
        assert r.duration == timedelta(seconds=1.0)

    def test_empty_report(self):
        r = ReflectionReport(
            versions_checked=0,
            detectors_used=(),
            findings=(),
            duration=timedelta(0),
        )
        assert r.versions_checked == 0
        assert len(r.findings) == 0

    def test_multiple_findings(self):
        f1 = make_finding()
        f2 = make_finding(reflection_type=ReflectionType.CONFLICT)
        r = make_report(findings=(f1, f2))
        assert len(r.findings) == 2

    def test_multiple_detectors(self):
        r = make_report(detectors_used=("DuplicateDetector", "ConflictDetector"))
        assert len(r.detectors_used) == 2


class TestReflectionReportImmutability:
    def test_frozen(self):
        r = make_report()
        with pytest.raises(AttributeError):
            r.versions_checked = 10

    def test_findings_frozen(self):
        r = make_report()
        with pytest.raises(AttributeError):
            r.findings = ()

    def test_detectors_used_frozen(self):
        r = make_report()
        with pytest.raises(AttributeError):
            r.detectors_used = ()


class TestReflectionReportValidation:
    def test_negative_versions_checked_raises(self):
        with pytest.raises(ValueError, match="versions_checked must be >= 0"):
            ReflectionReport(
                versions_checked=-1,
                detectors_used=(),
                findings=(),
                duration=timedelta(0),
            )
