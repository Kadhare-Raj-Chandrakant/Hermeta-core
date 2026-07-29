import pytest

from brain.runtime import create_memory_runtime, check_health, BrainHealthReport
from brain.runtime.health import BrainHealthReport


class TestHealthReport:
    def test_healthy_report(self):
        r = create_memory_runtime()
        report = check_health(r)
        assert isinstance(report, BrainHealthReport)
        assert report.healthy is True
        assert len(report.failures) == 0

    def test_all_components_reported(self):
        r = create_memory_runtime()
        report = check_health(r)
        expected = {"repository", "service", "session", "adapter", "validation", "retrieval", "reflection", "evolution", "detection", "learning", "publisher", "workflow"}
        assert set(report.components) == expected

    def test_unhealthy_report(self):
        from brain.runtime.runtime import BrainRuntime
        report = BrainHealthReport(
            healthy=False,
            components=("repository",),
            failures=("service", "session"),
        )
        assert report.healthy is False
        assert len(report.failures) == 2

    def test_report_is_frozen(self):
        r = create_memory_runtime()
        report = check_health(r)
        with pytest.raises(AttributeError):
            report.healthy = False


class TestCheckHealthFunction:
    def test_returns_brain_health_report(self):
        r = create_memory_runtime()
        report = check_health(r)
        assert isinstance(report, BrainHealthReport)

    def test_healthy_when_all_present(self):
        r = create_memory_runtime()
        report = check_health(r)
        assert report.healthy is True
