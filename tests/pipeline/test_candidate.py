from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence


def make_evidence() -> Evidence:
    return Evidence(source_type="conversation", content="test content")


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Redis for caching",
    understanding: str = "Use Redis for session caching",
    confidence: float = 0.9,
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        evidence_source=make_evidence(),
    )


class TestKnowledgeCandidateImmutability:
    def test_candidate_is_frozen(self):
        c = make_candidate()
        with pytest.raises(AttributeError):
            c.title = "other"

    def test_candidate_confidence_is_frozen(self):
        c = make_candidate()
        with pytest.raises(AttributeError):
            c.confidence = 0.5


class TestKnowledgeCandidateCreation:
    def test_create_with_defaults(self):
        c = make_candidate()
        assert c.knowledge_type == KnowledgeType.DECISION
        assert c.title == "Redis for caching"
        assert c.confidence == 0.9
        assert isinstance(c.detected_at, datetime)

    def test_create_with_explicit_timestamp(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        c = KnowledgeCandidate(
            knowledge_type=KnowledgeType.BUG,
            title="Bug",
            understanding="Found a bug",
            confidence=0.8,
            evidence_source=make_evidence(),
            detected_at=ts,
        )
        assert c.detected_at == ts

    def test_create_with_invalid_data(self):
        c = make_candidate(title="", confidence=1.5)
        assert c.title == ""
        assert c.confidence == 1.5


class TestKnowledgeCandidateEquality:
    def test_equal_instances(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        ev = make_evidence()
        c1 = KnowledgeCandidate(
            knowledge_type=KnowledgeType.DECISION,
            title="Redis",
            understanding="Use Redis",
            confidence=0.9,
            evidence_source=ev,
            detected_at=ts,
        )
        c2 = KnowledgeCandidate(
            knowledge_type=KnowledgeType.DECISION,
            title="Redis",
            understanding="Use Redis",
            confidence=0.9,
            evidence_source=ev,
            detected_at=ts,
        )
        assert c1 == c2

    def test_unequal_instances(self):
        ev = make_evidence()
        c1 = make_candidate(title="Redis")
        c2 = make_candidate(title="Postgres")
        assert c1 != c2
