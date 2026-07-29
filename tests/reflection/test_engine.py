import uuid
from datetime import datetime, timezone, timedelta

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.engine import ReflectionEngine
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport
from brain.reflection.type import ReflectionType
from brain.reflection.detectors.duplicate import DuplicateDetector
from brain.reflection.detectors.conflict import ConflictDetector
from brain.reflection.detectors.obsolete import ObsoleteDetector
from brain.reflection.detectors.gap import GapDetector


def make_version(
    title: str = "Test Knowledge",
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    understanding: str = "Test understanding",
    lifecycle_state: LifecycleState = LifecycleState.ACTIVE,
    evidence: tuple[Evidence, ...] = (Evidence(source="conversation", reference="proj/comp/file.md"),),
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=0.8,
        lifecycle_state=lifecycle_state,
        evidence=evidence,
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class StubDetector(ReflectionDetector):
    def __init__(self, findings: tuple[ReflectionFinding, ...]) -> None:
        self._findings = findings

    def analyze(self, versions: tuple[KnowledgeVersion, ...]) -> tuple[ReflectionFinding, ...]:
        return self._findings


class TestReflectionEngineCreation:
    def test_create_with_detectors(self):
        engine = ReflectionEngine(detectors=(DuplicateDetector(), ConflictDetector()))
        assert engine is not None

    def test_create_empty(self):
        engine = ReflectionEngine(detectors=())
        assert engine is not None


class TestReflectionEngineBehavior:
    def test_multiple_detectors(self):
        finding = ReflectionFinding(
            reflection_type=ReflectionType.GAP,
            affected_versions=(),
            explanation="Test gap",
            confidence=1.0,
        )
        engine = ReflectionEngine(detectors=(
            StubDetector(findings=(finding,)),
            StubDetector(findings=()),
            StubDetector(findings=(finding,)),
        ))
        versions = (make_version(),)
        report = engine.reflect(versions)
        assert len(report.findings) == 2
        assert report.detectors_used == ("StubDetector", "StubDetector", "StubDetector")

    def test_deterministic_ordering(self):
        finding = ReflectionFinding(
            reflection_type=ReflectionType.GAP,
            affected_versions=(),
            explanation="Test gap",
            confidence=1.0,
        )
        engine = ReflectionEngine(detectors=(StubDetector(findings=(finding,)),))
        r1 = engine.reflect(())
        r2 = engine.reflect(())
        assert r1.findings[0].id == r2.findings[0].id

    def test_immutable_report(self):
        engine = ReflectionEngine(detectors=())
        report = engine.reflect(())
        assert isinstance(report, ReflectionReport)
        with pytest.raises(AttributeError):
            report.versions_checked = 10

    def test_empty_input(self):
        engine = ReflectionEngine(detectors=(DuplicateDetector(),))
        report = engine.reflect(())
        assert report.versions_checked == 0
        assert isinstance(report.duration, timedelta)

    def test_versions_checked_count(self):
        engine = ReflectionEngine(detectors=())
        versions = (make_version(), make_version(), make_version())
        report = engine.reflect(versions)
        assert report.versions_checked == 3

    def test_real_detectors_integration(self):
        v1, v2 = make_duplicate_versions()
        engine = ReflectionEngine(detectors=(DuplicateDetector(),))
        report = engine.reflect((v1, v2))
        assert len(report.findings) >= 1
        assert report.detectors_used == ("DuplicateDetector",)

    def test_duration_is_positive(self):
        engine = ReflectionEngine(detectors=(DuplicateDetector(),))
        report = engine.reflect(())
        assert report.duration >= timedelta(0)


def make_duplicate_versions() -> tuple[KnowledgeVersion, KnowledgeVersion]:
    v1 = KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=KnowledgeType.DECISION,
        title="Database Architecture Decision",
        understanding="Use PostgreSQL",
        confidence=0.9,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(Evidence(source="conversation", reference="proj/db/arch.md"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )
    v2 = KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=KnowledgeType.DECISION,
        title="Database Architecture Selection",
        understanding="Use MongoDB",
        confidence=0.85,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(Evidence(source="conversation", reference="proj/db/arch.md"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )
    return v1, v2
