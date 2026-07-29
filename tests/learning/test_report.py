import pytest

from brain.learning.report import LearningReport
from datetime import timedelta


class TestLearningReport:
    def test_create_report(self):
        report = LearningReport(
            observations_processed=10,
            candidates_detected=5,
            accepted=3,
            rejected=2,
            events_processed=3,
            reflection_findings=1,
            transitions_created=1,
            duration=timedelta(seconds=0.5),
        )
        assert report.observations_processed == 10
        assert report.candidates_detected == 5
        assert report.accepted == 3
        assert report.rejected == 2
        assert report.events_processed == 3
        assert report.reflection_findings == 1
        assert report.transitions_created == 1
        assert report.duration == timedelta(seconds=0.5)

    def test_report_is_frozen(self):
        report = LearningReport(
            observations_processed=0,
            candidates_detected=0,
            accepted=0,
            rejected=0,
            events_processed=0,
            reflection_findings=0,
            transitions_created=0,
            duration=timedelta(0),
        )
        with pytest.raises(AttributeError):
            report.observations_processed = 5

    def test_empty_report(self):
        report = LearningReport(
            observations_processed=0,
            candidates_detected=0,
            accepted=0,
            rejected=0,
            events_processed=0,
            reflection_findings=0,
            transitions_created=0,
            duration=timedelta(0),
        )
        assert report.observations_processed == 0
        assert report.candidates_detected == 0
        assert report.accepted == 0
        assert report.rejected == 0
