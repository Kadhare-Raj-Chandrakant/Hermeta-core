import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence
from brain.domain.version import KnowledgeVersion
from brain.reflection.detectors.gap import GapDetector
from brain.reflection.type import ReflectionType


def make_version(knowledge_type: KnowledgeType = KnowledgeType.DECISION) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title="Test Knowledge",
        understanding="Test understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(Evidence(source="conversation", reference="proj/comp/file.md"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestGapDetector:
    def setup_method(self):
        self.detector = GapDetector()

    def test_missing_type_detected(self):
        findings = self.detector.analyze(())
        gap_types = [f.explanation for f in findings]
        assert any("architecture" in e for e in gap_types)
        assert any("decision" in e for e in gap_types)
        assert any("rule" in e for e in gap_types)

    def test_no_false_positives_when_all_present(self):
        versions = (
            make_version(KnowledgeType.ARCHITECTURE),
            make_version(KnowledgeType.DECISION),
            make_version(KnowledgeType.RULE),
        )
        findings = self.detector.analyze(versions)
        assert len(findings) == 0

    def test_partial_types(self):
        versions = (make_version(KnowledgeType.ARCHITECTURE),)
        findings = self.detector.analyze(versions)
        assert len(findings) == 2
        explanations = [f.explanation for f in findings]
        assert any("decision" in e for e in explanations)
        assert any("rule" in e for e in explanations)

    def test_custom_expected_types(self):
        detector = GapDetector(expected_types=(KnowledgeType.BUG,))
        findings = detector.analyze(())
        assert len(findings) == 1
        assert "bug" in findings[0].explanation

    def test_all_findings_are_gap_type(self):
        findings = self.detector.analyze(())
        for f in findings:
            assert f.reflection_type == ReflectionType.GAP

    def test_empty_versions(self):
        findings = self.detector.analyze(())
        assert all(f.affected_versions == () for f in findings)

    def test_deterministic_output(self):
        r1 = self.detector.analyze(())
        r2 = self.detector.analyze(())
        assert len(r1) == len(r2)
        for f1, f2 in zip(r1, r2):
            assert f1.explanation == f2.explanation
