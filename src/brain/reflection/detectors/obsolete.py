import uuid
from collections import defaultdict

from brain.domain.enums import LifecycleState
from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType


class ObsoleteDetector(ReflectionDetector):
    def analyze(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> tuple[ReflectionFinding, ...]:
        findings: list[ReflectionFinding] = []

        for v in versions:
            if v.lifecycle_state == LifecycleState.ARCHIVED:
                findings.append(ReflectionFinding(
                    reflection_type=ReflectionType.OBSOLETE,
                    affected_versions=(v.version_id,),
                    explanation=f"Knowledge is archived (lifecycle_state=ARCHIVED)",
                    confidence=0.8,
                ))

        by_identity: dict[uuid.UUID, list[KnowledgeVersion]] = defaultdict(list)
        for v in versions:
            by_identity[v.identity_id].append(v)

        for _identity_id, group in by_identity.items():
            if len(group) < 2:
                continue
            sorted_group = sorted(group, key=lambda v: v.version_number)
            newest = sorted_group[-1]
            for older in sorted_group[:-1]:
                if older.lifecycle_state != LifecycleState.ARCHIVED:
                    findings.append(ReflectionFinding(
                        reflection_type=ReflectionType.OBSOLETE,
                        affected_versions=(older.version_id, newest.version_id),
                        explanation=f"Older version (v{older.version_number}) exists alongside newer version (v{newest.version_number})",
                        confidence=0.6,
                    ))
        return tuple(findings)
