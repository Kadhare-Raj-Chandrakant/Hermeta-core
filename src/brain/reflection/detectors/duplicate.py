import uuid
import re
from collections import defaultdict

from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType


def _normalize_title(title: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", title.lower())
    return {w for w in words if len(w) >= 3}


class DuplicateDetector(ReflectionDetector):
    SIMILARITY_THRESHOLD = 0.5

    def analyze(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> tuple[ReflectionFinding, ...]:
        findings: list[ReflectionFinding] = []
        by_type: dict[str, list[KnowledgeVersion]] = defaultdict(list)
        for v in versions:
            by_type[v.knowledge_type.value].append(v)

        for _type_val, group in by_type.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a = group[i]
                    b = group[j]
                    words_a = _normalize_title(a.title)
                    words_b = _normalize_title(b.title)
                    if not words_a or not words_b:
                        continue
                    intersection = words_a & words_b
                    union = words_a | words_b
                    similarity = len(intersection) / len(union) if union else 0.0
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        findings.append(ReflectionFinding(
                            reflection_type=ReflectionType.DUPLICATE,
                            affected_versions=(a.version_id, b.version_id),
                            explanation=f"Titles share {len(intersection)}/{len(union)} significant words ({similarity:.0%} similarity)",
                            confidence=min(similarity, 1.0),
                        ))
        return tuple(findings)
