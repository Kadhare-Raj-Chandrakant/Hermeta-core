import pytest

from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.rules.type_rules import TypeRules
from brain.validation.result import ValidationResult


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Decision Title",
    understanding: str = "We decided X because of rationale and trade-offs",
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=0.8,
        evidence_source=Evidence(source_type="conversation", content="test"),
    )


class TestTypeRules:
    def test_decision_passes_with_tradeoffs(self):
        rule = TypeRules()
        result = rule.validate(make_candidate())
        assert result.passed is True
        assert result.rule_name == "TypeRules"

    def test_decision_fails_without_tradeoffs(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            understanding="We decided X because of rationale",
        ))
        assert result.passed is False
        assert "trade-offs" in result.reason

    def test_bug_passes_with_component_in_title(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.BUG,
            title="Auth Component Login Issue",
            understanding="Login fails",
        ))
        assert result.passed is True

    def test_bug_passes_with_component_in_understanding(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.BUG,
            title="Login Issue",
            understanding="Auth component login fails",
        ))
        assert result.passed is True

    def test_bug_fails_without_component(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.BUG,
            title="Login Issue",
            understanding="Login fails",
        ))
        assert result.passed is False
        assert "component" in result.reason

    def test_rule_passes_with_meaningful_title(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.RULE,
            title="Always validate user input",
            understanding="Validation is required",
        ))
        assert result.passed is True

    def test_rule_fails_with_short_title(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.RULE,
            title="Short",
            understanding="Validation is required",
        ))
        assert result.passed is False
        assert "meaningful title" in result.reason

    def test_pattern_type_passes(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.PATTERN,
            title="Test Pattern",
            understanding="We use pattern X",
        ))
        assert result.passed is True

    def test_discovery_type_passes(self):
        rule = TypeRules()
        result = rule.validate(make_candidate(
            knowledge_type=KnowledgeType.DISCOVERY,
            title="Test Discovery",
            understanding="We discovered X",
        ))
        assert result.passed is True
