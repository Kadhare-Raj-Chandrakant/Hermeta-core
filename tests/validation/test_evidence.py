import pytest
from unittest.mock import MagicMock

from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.result import ValidationResult


def make_candidate(source_type: str = "conversation") -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=KnowledgeType.DECISION,
        title="Test",
        understanding="Test understanding",
        confidence=0.8,
        evidence_source=Evidence(source_type=source_type, content="test"),
    )


def make_candidate_with_mock_source(source_type: str) -> KnowledgeCandidate:
    candidate = MagicMock(spec=KnowledgeCandidate)
    candidate.knowledge_type = KnowledgeType.DECISION
    candidate.title = "Test"
    candidate.understanding = "Test"
    candidate.confidence = 0.8
    mock_source = MagicMock()
    mock_source.source_type = source_type
    candidate.evidence_source = mock_source
    return candidate


class TestEvidenceRule:
    def test_passes_valid_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate())
        assert result.passed is True
        assert result.rule_name == "EvidenceRule"

    def test_passes_git_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate(source_type="git"))
        assert result.passed is True

    def test_passes_documentation_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate(source_type="documentation"))
        assert result.passed is True

    def test_fails_unknown_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate(source_type="unknown"))
        assert result.passed is False
        assert "Unknown source" in result.reason

    def test_fails_empty_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate_with_mock_source(""))
        assert result.passed is False

    def test_fails_whitespace_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate_with_mock_source("   "))
        assert result.passed is False

    def test_fails_none_source(self):
        class NoSourceCandidate:
            knowledge_type = KnowledgeType.DECISION
            title = "Test"
            understanding = "Test"
            confidence = 0.8
            evidence_source = None

        rule = EvidenceRule()
        result = rule.validate(NoSourceCandidate())
        assert result.passed is False
        assert "required" in result.reason

    def test_case_insensitive_source(self):
        rule = EvidenceRule()
        result = rule.validate(make_candidate(source_type="CONVERSATION"))
        assert result.passed is True
