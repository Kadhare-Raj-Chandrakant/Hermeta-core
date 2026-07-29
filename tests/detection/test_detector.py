import pytest

from brain.detection.detector import KnowledgeDetector
from brain.detection.observation import Observation
from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence


class RuleBasedDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        if "decision" in observation.content.lower():
            return (
                KnowledgeCandidate(
                    knowledge_type=KnowledgeType.DECISION,
                    title="Detected decision",
                    understanding="A decision was made",
                    confidence=0.8,
                    evidence_source=Evidence(source_type=observation.source_type, content=observation.content),
                ),
            )
        return ()


class MultiCandidateDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        return (
            KnowledgeCandidate(
                knowledge_type=KnowledgeType.PATTERN,
                title="Pattern one",
                understanding="First pattern",
                confidence=0.7,
                evidence_source=Evidence(source_type="test", content="one"),
            ),
            KnowledgeCandidate(
                knowledge_type=KnowledgeType.RULE,
                title="Rule two",
                understanding="Second rule",
                confidence=0.9,
                evidence_source=Evidence(source_type="test", content="two"),
            ),
        )


class TestDetectorInterfaceCompliance:
    def test_implements_interface(self):
        detector = RuleBasedDetector()
        assert isinstance(detector, KnowledgeDetector)

    def test_has_detect_method(self):
        detector = RuleBasedDetector()
        assert hasattr(detector, "detect")

    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            KnowledgeDetector()


class TestZeroCandidateScenarios:
    def test_no_match_returns_empty(self):
        detector = RuleBasedDetector()
        obs = Observation(source_type="test", content="no match here")
        result = detector.detect(obs)
        assert result == ()

    def test_empty_tuple_is_valid(self):
        detector = RuleBasedDetector()
        obs = Observation(source_type="test", content="nothing")
        result = detector.detect(obs)
        assert isinstance(result, tuple)
        assert len(result) == 0


class TestMultipleCandidateScenarios:
    def test_returns_multiple_candidates(self):
        detector = MultiCandidateDetector()
        obs = Observation(source_type="test", content="anything")
        result = detector.detect(obs)
        assert len(result) == 2

    def test_all_candidates_are_valid(self):
        detector = MultiCandidateDetector()
        obs = Observation(source_type="test", content="anything")
        result = detector.detect(obs)
        for candidate in result:
            assert isinstance(candidate, KnowledgeCandidate)


class TestDeterministicExecution:
    def test_same_input_same_output(self):
        detector = RuleBasedDetector()
        obs = Observation(source_type="test", content="we made a decision")
        r1 = detector.detect(obs)
        r2 = detector.detect(obs)
        assert len(r1) == len(r2)
        assert r1[0].title == r2[0].title

    def test_different_input_different_output(self):
        detector = RuleBasedDetector()
        obs1 = Observation(source_type="test", content="we made a decision")
        obs2 = Observation(source_type="test", content="nothing here")
        r1 = detector.detect(obs1)
        r2 = detector.detect(obs2)
        assert len(r1) != len(r2)
