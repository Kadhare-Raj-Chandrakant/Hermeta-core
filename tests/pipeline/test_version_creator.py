import uuid
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence
from brain.pipeline.version_creator import VersionCreator


def make_candidate(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Title",
    understanding: str = "Test understanding",
    confidence: float = 0.9,
) -> KnowledgeCandidate:
    return KnowledgeCandidate(
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        evidence_source=Evidence(source_type="conversation", content="test content"),
    )


class TestVersionCreatorSuccess:
    def test_creates_version_from_candidate(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        assert version.knowledge_type == KnowledgeType.DECISION
        assert version.title == "Test Title"
        assert version.understanding == "Test understanding"
        assert version.confidence == 0.9
        assert version.lifecycle_state == LifecycleState.ACTIVE

    def test_creates_with_provided_identity(self):
        creator = VersionCreator()
        candidate = make_candidate()
        identity_id = uuid.uuid4()
        version = creator.create(candidate, identity_id=identity_id)

        assert version.identity_id == identity_id

    def test_creates_with_generated_identity(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        assert isinstance(version.identity_id, uuid.UUID)

    def test_version_number_is_one(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        assert version.version_number == 1

    def test_evidence_populated_from_candidate(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        assert len(version.evidence) == 1
        assert version.evidence[0].source == "conversation"
        assert version.evidence[0].reference == "test content"

    def test_relationships_empty(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        assert version.relationships == ()


class TestVersionCreatorDeterminism:
    def test_same_input_same_output(self):
        creator = VersionCreator()
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        identity = uuid.uuid4()
        candidate = KnowledgeCandidate(
            knowledge_type=KnowledgeType.DECISION,
            title="Redis",
            understanding="Use Redis",
            confidence=0.9,
            evidence_source=Evidence(source_type="conversation", content="test"),
            detected_at=ts,
        )

        v1 = creator.create(candidate, identity_id=identity)
        v2 = creator.create(candidate, identity_id=identity)

        assert v1.identity_id == v2.identity_id
        assert v1.version_number == v2.version_number
        assert v1.knowledge_type == v2.knowledge_type
        assert v1.title == v2.title
        assert v1.understanding == v2.understanding
        assert v1.confidence == v2.confidence
        assert v1.lifecycle_state == v2.lifecycle_state
        assert v1.evidence == v2.evidence
        assert v1.created_at == v2.created_at

    def test_different_candidates_different_versions(self):
        creator = VersionCreator()
        c1 = make_candidate(title="Redis")
        c2 = make_candidate(title="Postgres")

        v1 = creator.create(c1)
        v2 = creator.create(c2)

        assert v1.title != v2.title


class TestVersionCreatorImmutability:
    def test_created_version_is_frozen(self):
        creator = VersionCreator()
        candidate = make_candidate()
        version = creator.create(candidate)

        with pytest.raises(AttributeError):
            version.title = "other"


import pytest
