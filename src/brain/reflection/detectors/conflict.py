import uuid
from collections import defaultdict

from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType


class ConflictDetector(ReflectionDetector):
    def analyze(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> tuple[ReflectionFinding, ...]:
        findings: list[ReflectionFinding] = []
        by_scope: dict[tuple, list[KnowledgeVersion]] = defaultdict(list)
        for v in versions:
            evidence = v.evidence
            project = ""
            component = ""
            for e in evidence:
                parts = e.reference.split("/") if e.reference else []
                if len(parts) >= 2:
                    project = parts[0]
                    component = parts[1]
            scope_key = (v.knowledge_type.value, project, component)
            by_scope[scope_key].append(v)

        for _scope_key, group in by_scope.items():
            if len(group) < 2:
                continue
            summaries = [(v.version_id, v.understanding.strip().lower()) for v in group]
            for i in range(len(summaries)):
                for j in range(i + 1, len(summaries)):
                    vid_a, summary_a = summaries[i]
                    vid_b, summary_b = summaries[j]
                    if summary_a != summary_b:
                        findings.append(ReflectionFinding(
                            reflection_type=ReflectionType.CONFLICT,
                            affected_versions=(vid_a, vid_b),
                            explanation=f"Same scope with different conclusions",
                            confidence=0.7,
                        ))
        return tuple(findings)
