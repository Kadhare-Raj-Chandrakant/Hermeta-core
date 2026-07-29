import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.reflection.detectors.obsolete import ObsoleteDetector
from brain.reflection.type import ReflectionType


def make_version(
    lifecycle_state: LifecycleState = LifecycleState.ACTIVE,
    version_number: int = 1,
    identity_id: uuid.UUID | None = None,
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id or uuid.uuid4(),
        version_number=version_number,
        knowledge_type=KnowledgeType.PATTERN,
        title="Test Knowledge",
        understanding="Test understanding",
        confidence=0.8,
        lifecycle_state=lifecycle_state,
        evidence=(Evidence(source="conversation", reference="proj/pattern.md"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestObsoleteDetector:
    def setup_method(self):
        self.detector = ObsoleteDetector()

    def test_archived_detection(self):
        v = make_version(lifecycle_state=LifecycleState.ARCHIVED)
        findings = self.detector.analyze((v,))
        assert len(findings) == 1
        assert findings[0].reflection_type == ReflectionType.OBSOLETE
        assert v.version_id in findings[0].affected_versions

    def test_older_version_detection(self):
        identity = uuid.uuid4()
        old = make_version(version_number=1, identity_id=identity)
        new = make_version(version_number=2, identity_id=identity)
        findings = self.detector.analyze((old, new))
        obsolete_findings = [f for f in findings if f.reflection_type == ReflectionType.OBSOLETE]
        assert len(obsolete_findings) == 1
        assert old.version_id in obsolete_findings[0].affected_versions
        assert new.version_id in obsolete_findings[0].affected_versions

    def test_single_version_no_obsolete(self):
        v = make_version()
        findings = self.detector.analyze((v,))
        assert len(findings) == 0

    def test_different_identities_no_obsolete(self):
        v1 = make_version()
        v2 = make_version()
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_archived_triggers_even_with_newer(self):
        identity = uuid.uuid4()
        old = make_version(version_number=1, identity_id=identity, lifecycle_state=LifecycleState.ARCHIVED)
        new = make_version(version_number=2, identity_id=identity)
        findings = self.detector.analyze((old, new))
        version_ids_in_findings = set()
        for f in findings:
            version_ids_in_findings.update(f.affected_versions)
        assert old.version_id in version_ids_in_findings

    def test_empty_versions(self):
        findings = self.detector.analyze(())
        assert len(findings) == 0

    def test_deterministic_output(self):
        v = make_version(lifecycle_state=LifecycleState.ARCHIVED)
        r1 = self.detector.analyze((v,))
        r2 = self.detector.analyze((v,))
        assert r1[0].affected_versions == r2[0].affected_versions
