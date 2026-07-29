import pytest

from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.result import ValidationResult


def make_candidate(
    title: str = "Test Title",
    understanding: str = "Test understanding with rationale",
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=0.8,
        evidence_source=Evidence(source_type="conversation", content="test"),
    )


class TestCompletenessRule:
    def test_passes_valid_candidate(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate())
        assert result.passed is True
        assert result.rule_name == "CompletenessRule"

    def test_fails_empty_title(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(title=""))
        assert result.passed is False
        assert "title" in result.reason

    def test_fails_whitespace_title(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(title="   "))
        assert result.passed is False

    def test_fails_empty_understanding(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(understanding=""))
        assert result.passed is False
        assert "understanding" in result.reason

    def test_fails_decision_without_rationale(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.DECISION,
            understanding="We decided X",
        ))
        assert result.passed is False
        assert "rationale" in result.reason

    def test_passes_decision_with_rationale(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.DECISION,
            understanding="We decided X because of rationale and trade-offs",
        ))
        assert result.passed is True

    def test_non_decision_types_not_affected(self):
        rule = CompletenessRule()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.PATTERN,
            understanding="We use pattern X",
        ))
        assert result.passed is True
