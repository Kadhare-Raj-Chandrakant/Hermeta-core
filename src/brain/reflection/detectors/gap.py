import uuid
from collections import defaultdict

from brain.domain.enums import KnowledgeType
from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType


class GapDetector(ReflectionDetector):
    def __init__(
        self,
        expected_types: tuple[KnowledgeType, ...] = (
            KnowledgeType.ARCHITECTURE,
            KnowledgeType.DECISION,
            KnowledgeType.RULE,
        ),
    ) -> None:
        self._expected_types = expected_types

    def analyze(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> tuple[ReflectionFinding, ...]:
        present_types: set[KnowledgeType] = {v.knowledge_type for v in versions}
        findings: list[ReflectionFinding] = []
        for expected in self._expected_types:
            if expected not in present_types:
                findings.append(ReflectionFinding(
                    reflection_type=ReflectionType.GAP,
                    affected_versions=(),
                    explanation=f"Missing knowledge of type {expected.value}",
                    confidence=1.0,
                ))
        return tuple(findings)
