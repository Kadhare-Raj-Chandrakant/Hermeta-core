import pytest

from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.engine import ValidationEngine
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule
from brain.validation.report import ValidationReport
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.rules.type_rules import TypeRules


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Decision",
    understanding: str = "We decided X because of rationale and trade-offs",
    confidence: float = 0.8,
    source_type: str = "conversation",
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        evidence_source=Evidence(source_type=source_type, content="test"),
    )


class PassingRule(ValidationRule):
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        return ValidationResult(passed=True, rule_name="PassingRule", reason="always passes")


class FailingRule(ValidationRule):
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        return ValidationResult(passed=False, rule_name="FailingRule", reason="always fails")


class TestValidationEngine:
    def test_empty_rules_passes(self):
        engine = ValidationEngine(rules=())
        report = engine.validate(make_candidate())
        assert report.passed is True
        assert len(report.results) == 0

    def test_single_passing_rule(self):
        engine = ValidationEngine(rules=(PassingRule(),))
        report = engine.validate(make_candidate())
        assert report.passed is True
        assert len(report.results) == 1

    def test_single_failing_rule(self):
        engine = ValidationEngine(rules=(FailingRule(),))
        report = engine.validate(make_candidate())
        assert report.passed is False
        assert len(report.results) == 1

    def test_multiple_rules_all_pass(self):
        engine = ValidationEngine(rules=(PassingRule(), PassingRule(), PassingRule()))
        report = engine.validate(make_candidate())
        assert report.passed is True
        assert len(report.results) == 3

    def test_multiple_rules_one_fails(self):
        engine = ValidationEngine(rules=(PassingRule(), FailingRule(), PassingRule()))
        report = engine.validate(make_candidate())
        assert report.passed is False

    def test_multiple_rules_all_fail(self):
        engine = ValidationEngine(rules=(FailingRule(), FailingRule()))
        report = engine.validate(make_candidate())
        assert report.passed is False
        assert len(report.results) == 2

    def test_deterministic_order(self):
        engine = ValidationEngine(rules=(PassingRule(), FailingRule()))
        r1 = engine.validate(make_candidate())
        r2 = engine.validate(make_candidate())
        assert [r.rule_name for r in r1.results] == [r.rule_name for r in r2.results]

    def test_custom_injected_rule(self):
        class CustomRule(ValidationRule):
            def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
                if candidate.confidence > 0.5:
                    return ValidationResult(passed=True, rule_name="Custom", reason="high confidence")
                return ValidationResult(passed=False, rule_name="Custom", reason="low confidence")

        engine = ValidationEngine(rules=(CustomRule(),))
        report = engine.validate(make_candidate(confidence=0.8))
        assert report.passed is True

        report = engine.validate(make_candidate(confidence=0.3))
        assert report.passed is False

    def test_report_is_frozen(self):
        engine = ValidationEngine(rules=())
        report = engine.validate(make_candidate())
        with pytest.raises(AttributeError):
            report.passed = False


class TestDefaultRules:
    def test_confidence_rule_passes(self):
        engine = ValidationEngine(rules=(ConfidenceRule(threshold=0.3),))
        report = engine.validate(make_candidate(confidence=0.5))
        assert report.passed is True

    def test_confidence_rule_fails(self):
        engine = ValidationEngine(rules=(ConfidenceRule(threshold=0.5),))
        report = engine.validate(make_candidate(confidence=0.3))
        assert report.passed is False

    def test_completeness_rule_passes(self):
        engine = ValidationEngine(rules=(CompletenessRule(),))
        report = engine.validate(make_candidate())
        assert report.passed is True

    def test_completeness_rule_fails_empty_title(self):
        engine = ValidationEngine(rules=(CompletenessRule(),))
        report = engine.validate(make_candidate(title=""))
        assert report.passed is False

    def test_evidence_rule_passes(self):
        engine = ValidationEngine(rules=(EvidenceRule(),))
        report = engine.validate(make_candidate())
        assert report.passed is True

    def test_evidence_rule_fails_unknown_source(self):
        engine = ValidationEngine(rules=(EvidenceRule(),))
        report = engine.validate(make_candidate(source_type="unknown_source"))
        assert report.passed is False

    def test_type_rules_decision_passes(self):
        engine = ValidationEngine(rules=(TypeRules(),))
        report = engine.validate(make_candidate(
            knowledge_type=KnowledgeType.DECISION,
            understanding="We decided X because of rationale and trade-offs",
        ))
        assert report.passed is True

    def test_type_rules_decision_fails_no_tradeoffs(self):
        engine = ValidationEngine(rules=(TypeRules(),))
        report = engine.validate(make_candidate(
            knowledge_type=KnowledgeType.DECISION,
            understanding="We decided X because of rationale",
        ))
        assert report.passed is False

    def test_all_default_rules_together(self):
        engine = ValidationEngine(rules=(
            ConfidenceRule(threshold=0.3),
            CompletenessRule(),
            EvidenceRule(),
            TypeRules(),
        ))
        report = engine.validate(make_candidate())
        assert report.passed is True

    def test_all_default_rules_reject_bad_candidate(self):
        engine = ValidationEngine(rules=(
            ConfidenceRule(threshold=0.5),
            CompletenessRule(),
            EvidenceRule(),
            TypeRules(),
        ))
        report = engine.validate(make_candidate(confidence=0.1))
        assert report.passed is False
