import pytest

from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.result import ValidationResult


def make_candidate(confidence: float = 0.8) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=KnowledgeType.DECISION,
        title="Test",
        understanding="Test understanding",
        confidence=confidence,
        evidence_source=Evidence(source_type="conversation", content="test"),
    )


class TestConfidenceRule:
    def test_passes_above_threshold(self):
        rule = ConfidenceRule(threshold=0.3)
        result = rule.validate(make_candidate(confidence=0.5))
        assert result.passed is True
        assert result.rule_name == "ConfidenceRule"

    def test_passes_at_threshold(self):
        rule = ConfidenceRule(threshold=0.5)
        result = rule.validate(make_candidate(confidence=0.5))
        assert result.passed is True

    def test_fails_below_threshold(self):
        rule = ConfidenceRule(threshold=0.5)
        result = rule.validate(make_candidate(confidence=0.3))
        assert result.passed is False
        assert "below threshold" in result.reason

    def test_default_threshold(self):
        rule = ConfidenceRule()
        result = rule.validate(make_candidate(confidence=0.2))
        assert result.passed is False

    def test_custom_threshold(self):
        rule = ConfidenceRule(threshold=0.9)
        result = rule.validate(make_candidate(confidence=0.8))
        assert result.passed is False

    def test_result_is_immutable(self):
        rule = ConfidenceRule()
        result = rule.validate(make_candidate())
        with pytest.raises(AttributeError):
            result.passed = False
