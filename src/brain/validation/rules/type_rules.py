from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.validation.result import ValidationResult
from brain.validation.rule import ValidationRule


class TypeRules(ValidationRule):
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        knowledge_type = candidate.knowledge_type

        if knowledge_type == KnowledgeType.DECISION:
            if not candidate.understanding or "trade" not in candidate.understanding.lower():
                return ValidationResult(
                    passed=False,
                    rule_name="TypeRules",
                    reason="DECISION type requires understanding containing trade-offs",
                )

        if knowledge_type == KnowledgeType.BUG:
            if not candidate.title or "component" not in candidate.title.lower():
                if not candidate.understanding or "component" not in candidate.understanding.lower():
                    return ValidationResult(
                        passed=False,
                        rule_name="TypeRules",
                        reason="BUG type requires component information in title or understanding",
                    )

        if knowledge_type == KnowledgeType.RULE:
            if not candidate.title or len(candidate.title.strip()) < 10:
                return ValidationResult(
                    passed=False,
                    rule_name="TypeRules",
                    reason="RULE type requires meaningful title (at least 10 characters)",
                )

        return ValidationResult(
            passed=True,
            rule_name="TypeRules",
            reason="Type requirements satisfied",
        )
