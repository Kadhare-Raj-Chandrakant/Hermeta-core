from brain.pipeline.candidate import KnowledgeCandidate
from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class TestValidationRuleInterface:
    def test_cannot_instantiate_abstract(self):
        import pytest
        with pytest.raises(TypeError):
            ValidationRule()

    def test_implements_interface(self):
        class DummyRule(ValidationRule):
            def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
                return ValidationResult(passed=True, rule_name="Dummy", reason="ok")

        rule = DummyRule()
        assert isinstance(rule, ValidationRule)

    def test_has_validate_method(self):
        class DummyRule(ValidationRule):
            def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
                return ValidationResult(passed=True, rule_name="Dummy", reason="ok")

        rule = DummyRule()
        assert hasattr(rule, "validate")


class TestValidationResult:
    def test_create_success_result(self):
        result = ValidationResult(passed=True, rule_name="TestRule", reason="All good")
        assert result.passed is True
        assert result.rule_name == "TestRule"
        assert result.reason == "All good"

    def test_create_failure_result(self):
        result = ValidationResult(passed=False, rule_name="TestRule", reason="Failed")
        assert result.passed is False

    def test_result_is_frozen(self):
        import pytest
        result = ValidationResult(passed=True, rule_name="Test", reason="ok")
        with pytest.raises(AttributeError):
            result.passed = False
