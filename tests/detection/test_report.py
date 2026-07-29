from datetime import timedelta

import pytest

from brain.detection.report import DetectionReport
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence as PipelineEvidence
from brain.domain.enums import KnowledgeType


def make_candidate(title: str = "Test") -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=KnowledgeType.DECISION,
        title=title,
        understanding="Test understanding",
        confidence=0.8,
        evidence_source=PipelineEvidence(source_type="conversation", content="test"),
    )


class TestDetectionReportCreation:
    def test_create_report(self):
        report = DetectionReport(
            observations_processed=5,
            candidates_produced=3,
            candidates=(make_candidate("A"), make_candidate("B"), make_candidate("C")),
            detectors_used=("RuleDetector", "LLMDetector"),
            duration=timedelta(seconds=1.5),
        )
        assert report.observations_processed == 5
        assert report.candidates_produced == 3
        assert len(report.candidates) == 3
        assert report.detectors_used == ("RuleDetector", "LLMDetector")
        assert report.duration == timedelta(seconds=1.5)

    def test_empty_report(self):
        report = DetectionReport(
            observations_processed=0,
            candidates_produced=0,
            candidates=(),
            detectors_used=(),
            duration=timedelta(0),
        )
        assert report.observations_processed == 0
        assert report.candidates_produced == 0
        assert len(report.candidates) == 0


class TestDetectionReportImmutability:
    def test_report_is_frozen(self):
        report = DetectionReport(
            observations_processed=1,
            candidates_produced=0,
            candidates=(),
            detectors_used=(),
            duration=timedelta(0),
        )
        with pytest.raises(AttributeError):
            report.observations_processed = 5

    def test_candidates_tuple_is_immutable(self):
        report = DetectionReport(
            observations_processed=1,
            candidates_produced=1,
            candidates=(make_candidate(),),
            detectors_used=("D",),
            duration=timedelta(0),
        )
        with pytest.raises(AttributeError):
            report.candidates = ()
