from dataclasses import dataclass

from brain.pipeline.candidate import KnowledgeCandidate


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


class CandidateValidator:
    def validate(self, candidate: KnowledgeCandidate) -> ValidationResult:
        errors: list[str] = []

        if not candidate.knowledge_type:
            errors.append("knowledge_type is required")

        if not candidate.title or not candidate.title.strip():
            errors.append("title is required")

        if not candidate.understanding or not candidate.understanding.strip():
            errors.append("understanding is required")

        if not 0.0 <= candidate.confidence <= 1.0:
            errors.append(f"confidence must be between 0.0 and 1.0, got {candidate.confidence}")

        if not candidate.evidence_source:
            errors.append("evidence_source is required")

        return ValidationResult(is_valid=len(errors) == 0, errors=tuple(errors))
