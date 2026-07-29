import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.reflection.detectors.duplicate import DuplicateDetector, _normalize_title
from brain.reflection.type import ReflectionType


def make_version(
    title: str = "Test Knowledge",
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title=title,
        understanding="Test understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(Evidence(source="conversation", reference="proj/comp/file.md"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestNormalizeTitle:
    def test_basic(self):
        result = _normalize_title("Database Architecture Decision")
        assert "database" in result
        assert "architecture" in result
        assert "decision" in result

    def test_short_words_excluded(self):
        result = _normalize_title("A Big Is The")
        assert "a" not in result
        assert "is" not in result
        assert "big" in result

    def test_case_insensitive(self):
        result = _normalize_title("DATABASE ARCHITECTURE")
        assert result == {"database", "architecture"}

    def test_punctuation_removed(self):
        result = _normalize_title("hello-world, test!")
        assert "hello" in result
        assert "world" in result
        assert "test" in result


class TestDuplicateDetector:
    def setup_method(self):
        self.detector = DuplicateDetector()

    def test_detects_duplicates(self):
        v1 = make_version(title="Database Architecture Decision")
        v2 = make_version(title="Database Architecture Selection")
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 1
        assert findings[0].reflection_type == ReflectionType.DUPLICATE
        assert v1.version_id in findings[0].affected_versions
        assert v2.version_id in findings[0].affected_versions

    def test_different_type_ignored(self):
        v1 = make_version(title="Database Architecture", knowledge_type=KnowledgeType.DECISION)
        v2 = make_version(title="Database Architecture", knowledge_type=KnowledgeType.PATTERN)
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_deterministic_output(self):
        v1 = make_version(title="Database Architecture Decision")
        v2 = make_version(title="Database Architecture Selection")
        r1 = self.detector.analyze((v1, v2))
        r2 = self.detector.analyze((v1, v2))
        assert len(r1) == len(r2)
        assert r1[0].affected_versions == r2[0].affected_versions

    def test_no_duplicates(self):
        v1 = make_version(title="Database Architecture")
        v2 = make_version(title="User Authentication Flow")
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 0

    def test_identical_title_treated_as_duplicate(self):
        v1 = make_version(title="Database Architecture")
        v2 = make_version(title="Database Architecture")
        findings = self.detector.analyze((v1, v2))
        assert len(findings) == 1

    def test_empty_versions(self):
        findings = self.detector.analyze(())
        assert len(findings) == 0

    def test_single_version(self):
        v1 = make_version(title="Database Architecture")
        findings = self.detector.analyze((v1,))
        assert len(findings) == 0

    def test_three_versions(self):
        v1 = make_version(title="Database Architecture Decision")
        v2 = make_version(title="Database Architecture Selection")
        v3 = make_version(title="Database Architecture Choice")
        findings = self.detector.analyze((v1, v2, v3))
        assert len(findings) == 3
