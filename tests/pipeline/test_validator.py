from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence
from brain.pipeline.validator import CandidateValidator, ValidationResult


def make_evidence() -> Evidence:
    return Evidence(source_type="conversation", content="test content")


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Title",
    understanding: str = "Test understanding",
    confidence: float = 0.9,
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        evidence_source=make_evidence(),
    )


class TestValidatorSuccess:
    def test_valid_candidate_passes(self):
        validator = CandidateValidator()
        result = validator.validate(make_candidate())
        assert result.is_valid is True
        assert result.errors == ()

    def test_boundary_confidence_passes(self):
        validator = CandidateValidator()
        low = make_candidate(confidence=0.0)
        high = make_candidate(confidence=1.0)
        assert validator.validate(low).is_valid is True
        assert validator.validate(high).is_valid is True


class TestValidatorFailure:
    def test_empty_title_fails(self):
        validator = CandidateValidator()
        c = make_candidate(title="")
        result = validator.validate(c)
        assert result.is_valid is False
        assert any("title" in e for e in result.errors)

    def test_empty_understanding_fails(self):
        validator = CandidateValidator()
        c = make_candidate(understanding="")
        result = validator.validate(c)
        assert result.is_valid is False
        assert any("understanding" in e for e in result.errors)

    def test_confidence_out_of_range_fails(self):
        validator = CandidateValidator()
        c = make_candidate(confidence=1.5)
        result = validator.validate(c)
        assert result.is_valid is False
        assert any("confidence" in e for e in result.errors)

    def test_negative_confidence_fails(self):
        validator = CandidateValidator()
        c = make_candidate(confidence=-0.1)
        result = validator.validate(c)
        assert result.is_valid is False
        assert any("confidence" in e for e in result.errors)


class TestValidatorImmutability:
    def test_result_is_frozen(self):
        validator = CandidateValidator()
        result = validator.validate(make_candidate())
        with pytest.raises(AttributeError):
            result.is_valid = False

    def test_errors_is_frozen(self):
        validator = CandidateValidator()
        result = validator.validate(make_candidate())
        with pytest.raises(AttributeError):
            result.errors = ("new error",)


import pytest
