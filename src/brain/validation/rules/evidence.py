from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class EvidenceRule(ValidationRule):
    VALID_SOURCES = frozenset({
        "conversation",
        "git",
        "documentation",
        "ide",
        "code_review",
        "meeting",
        "email",
        "observation",
        "execution",
    })

    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        if not candidate.evidence_source:
            return ValidationResult(
                passed=False,
                rule_name="EvidenceRule",
                reason="evidence_source is required",
            )

        source_type = candidate.evidence_source.source_type
        if not source_type or not source_type.strip():
            return ValidationResult(
                passed=False,
                rule_name="EvidenceRule",
                reason="evidence_source.source_type must not be empty",
            )

        if source_type.lower() not in self.VALID_SOURCES:
            return ValidationResult(
                passed=False,
                rule_name="EvidenceRule",
                reason=f"Unknown source type: {source_type}",
            )

        return ValidationResult(
            passed=True,
            rule_name="EvidenceRule",
            reason="Evidence accepted",
        )
