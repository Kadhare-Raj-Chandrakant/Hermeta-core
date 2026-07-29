from brain.detection.detector import KnowledgeDetector
from brain.detection.observation import Observation
from brain.detection.pipeline import DetectionPipeline
from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence


def make_observation(content: str = "test content") -> Observation:
    return Observation(source_type="conversation", content=content)


def make_candidate(title: str = "Test") -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=KnowledgeType.DECISION,
        title=title,
        understanding="Test understanding",
        confidence=0.8,
        evidence_source=Evidence(source_type="conversation", content="test"),
    )


class SuccessfulDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        return (make_candidate("From " + observation.source_type),)


class EmptyDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        return ()


class TestMultipleDetectorOrchestration:
    def test_two_detectors_both_run(self):
        d1 = SuccessfulDetector()
        d2 = SuccessfulDetector()

        pipeline = DetectionPipeline(detectors=(d1, d2))
        report = pipeline.run((make_observation(),))

        assert report.candidates_produced == 2
        assert len(report.candidates) == 2

    def test_detectors_run_in_order(self):
        call_order = []

        class TrackingDetector(KnowledgeDetector):
            def __init__(self, name: str) -> None:
                self._name = name

            def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
                call_order.append(self._name)
                return ()

        pipeline = DetectionPipeline(
            detectors=(TrackingDetector("A"), TrackingDetector("B"), TrackingDetector("C")),
        )
        pipeline.run((make_observation(),))

        assert call_order == ["A", "B", "C"]


class TestZeroCandidateScenarios:
    def test_empty_detectors_returns_empty_report(self):
        pipeline = DetectionPipeline(detectors=())
        report = pipeline.run((make_observation(),))

        assert report.observations_processed == 1
        assert report.candidates_produced == 0
        assert len(report.candidates) == 0

    def test_detector_returns_nothing(self):
        pipeline = DetectionPipeline(detectors=(EmptyDetector(),))
        report = pipeline.run((make_observation(),))

        assert report.candidates_produced == 0
        assert len(report.candidates) == 0


class TestMultipleCandidateScenarios:
    def test_multiple_observations_multiple_detectors(self):
        pipeline = DetectionPipeline(detectors=(SuccessfulDetector(),))
        report = pipeline.run((make_observation("one"), make_observation("two")))

        assert report.observations_processed == 2
        assert report.candidates_produced == 2
        assert len(report.candidates) == 2


class TestDeterministicExecutionOrder:
    def test_same_input_same_output(self):
        pipeline = DetectionPipeline(detectors=(SuccessfulDetector(),))
        obs = make_observation()
        r1 = pipeline.run((obs,))
        r2 = pipeline.run((obs,))

        assert r1.candidates_produced == r2.candidates_produced
        assert r1.observations_processed == r2.observations_processed


class TestPipelineExtensibility:
    def test_custom_detector_works(self):
        class CustomDetector(KnowledgeDetector):
            def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
                return (
                    KnowledgeCandidate(
                        knowledge_type=KnowledgeType.ASSUMPTION,
                        title="Custom",
                        understanding="Custom detection",
                        confidence=0.6,
                        evidence_source=Evidence(source_type="custom", content="data"),
                    ),
                )

        pipeline = DetectionPipeline(detectors=(CustomDetector(),))
        report = pipeline.run((make_observation(),))

        assert report.candidates_produced == 1
        assert len(report.candidates) == 1


class TestDetectionReportCorrectness:
    def test_report_counts(self):
        pipeline = DetectionPipeline(
            detectors=(SuccessfulDetector(), EmptyDetector()),
        )
        report = pipeline.run((make_observation("a"), make_observation("b")))

        assert report.observations_processed == 2
        assert report.candidates_produced == 2
        assert len(report.candidates) == 2
        assert report.detectors_used == ("SuccessfulDetector", "EmptyDetector")

    def test_report_duration_positive(self):
        pipeline = DetectionPipeline(detectors=(SuccessfulDetector(),))
        report = pipeline.run((make_observation(),))

        assert report.duration.total_seconds() >= 0


class TestDependencyInjection:
    def test_all_collaborators_injected(self):
        detector = SuccessfulDetector()

        pipeline = DetectionPipeline(
            detectors=(detector,),
        )

        assert pipeline._detectors == (detector,)


class TestNoCouplingToBrainService:
    def test_pipeline_does_not_import_brain_service(self):
        import brain.detection.pipeline as mod
        source = mod.__file__
        with open(source) as f:
            content = f.read()
        assert "brain_service" not in content.lower()
        assert "BrainService" not in content
        assert "repository" not in content.lower()

    def test_pipeline_does_not_import_validation_engine(self):
        import brain.detection.pipeline as mod
        source = mod.__file__
        with open(source) as f:
            content = f.read()
        assert "ValidationEngine" not in content
        assert "CandidateValidator" not in content
