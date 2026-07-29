import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.reflection.detectors.conflict import ConflictDetector
from brain.reflection.type import ReflectionType


def make_version(
    understanding: str = "Test understanding",
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    evidence: tuple[Evidence, ...] = (Evidence(source="conversation", reference="proj/api/design.md"),),
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title="Test",
        understanding=understanding,
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=evidence,
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestConflictDetector:
    def setup_method(self):
        self.detector = ConflictDetector()

    def test_detects_conflict(self):
        v1 = make_version(understanding="REST is the best choice")
        v2 = make_version(understanding="GraphQL is the best choice")
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 1
        assert findings[0].reflection_type == ReflectionType.CONFLICT
        assert v1.version_id in findings[0].affected_versions
        assert v2.version_id in findings[0].affected_versions

    def test_same_scope_same_conclusion_no_conflict(self):
        v1 = make_version(understanding="REST is the best choice")
        v2 = make_version(understanding="REST is the best choice")
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_different_scope_no_conflict(self):
        v1 = make_version(
            understanding="REST is the best",
            evidence=(Evidence(source="conversation", reference="proj/api/design.md"),),
        )
        v2 = make_version(
            understanding="GraphQL is the best",
            evidence=(Evidence(source="conversation", reference="proj/db/design.md"),),
        )
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_unrelated_knowledge_ignored(self):
        v1 = make_version(understanding="Use REST", knowledge_type=KnowledgeType.DECISION)
        v2 = make_version(understanding="Use GraphQL", knowledge_type=KnowledgeType.PATTERN)
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_empty_versions(self):
        findings = self.detector.analyze(())
        assert len(findings) == 0

    def test_single_version(self):
        v1 = make_version(understanding="Test")
        findings = self.detector.analyze((v1,))
        assert len(findings) == 0

    def test_deterministic_output(self):
        v1 = make_version(understanding="REST is the best")
        v2 = make_version(understanding="GraphQL is the best")
        r1 = self.detector.analyze((v1, v2))
        r2 = self.detector.analyze((v1, v2))
        assert r1[0].affected_versions == r2[0].affected_versions
