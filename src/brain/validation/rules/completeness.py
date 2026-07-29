from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class CompletenessRule(ValidationRule):
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        errors: list[str] = []

        if not candidate.title or not candidate.title.strip():
            errors.append("title is required")

        if not candidate.understanding or not candidate.understanding.strip():
            errors.append("understanding is required")

        if candidate.knowledge_type == KnowledgeType.DECISION:
            if not candidate.understanding or "rationale" not in candidate.understanding.lower():
                errors.append("DECISION type requires understanding containing rationale")

        if errors:
            return ValidationResult(
                passed=False,
                rule_name="CompletenessRule",
                reason="; ".join(errors),
            )

        return ValidationResult(
            passed=True,
            rule_name="CompletenessRule",
            reason="Completeness accepted",
        )
