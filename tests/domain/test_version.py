import pytest
from datetime import datetime, timezone
import uuid

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.identity import KnowledgeIdentity
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion


def create_version(
    identity_id: uuid.UUID,
    version_number: int = 1,
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Knowledge",
    understanding: str = "Test understanding",
    confidence: float = 0.8,
    lifecycle_state: LifecycleState = LifecycleState.DRAFT,
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id,
        version_number=version_number,
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=confidence,
        lifecycle_state=lifecycle_state,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestKnowledgeVersionImmutability:
    def test_version_is_frozen(self):
        identity = KnowledgeIdentity.create()
        version = create_version(identity.id)
        with pytest.raises(AttributeError):
            version.title = "New Title"

    def test_version_identity_id_is_frozen(self):
        identity = KnowledgeIdentity.create()
        version = create_version(identity.id)
        with pytest.raises(AttributeError):
            version.identity_id = uuid.uuid4()

    def test_version_number_is_frozen(self):
        identity = KnowledgeIdentity.create()
        version = create_version(identity.id)
        with pytest.raises(AttributeError):
            version.version_number = 2

    def test_version_evidence_tuple_is_immutable(self):
        identity = KnowledgeIdentity.create()
        evidence = (Evidence(source="test", reference="ref"),)
        version = KnowledgeVersion(
            identity_id=identity.id,
            version_number=1,
            knowledge_type=KnowledgeType.DECISION,
            title="Test",
            understanding="Test",
            confidence=0.8,
            lifecycle_state=LifecycleState.DRAFT,
            evidence=evidence,
            relationships=(),
            created_at=datetime.now(timezone.utc),
        )
        with pytest.raises(AttributeError):
            version.evidence = ()


class TestKnowledgeVersionIdentityStability:
    def test_multiple_versions_share_identity(self):
        identity = KnowledgeIdentity.create()
        v1 = create_version(identity.id, version_number=1)
        v2 = create_version(identity.id, version_number=2)
        v3 = create_version(identity.id, version_number=3)

        assert v1.identity_id == v2.identity_id == v3.identity_id == identity.id

    def test_versions_are_distinct_objects(self):
        identity = KnowledgeIdentity.create()
        v1 = create_version(identity.id, version_number=1)
        v2 = create_version(identity.id, version_number=2)

        assert v1 is not v2
        assert v1.version_number != v2.version_number


class TestKnowledgeVersionId:
    def test_version_id_auto_generated(self):
        identity = KnowledgeIdentity.create()
        v = create_version(identity.id)
        assert isinstance(v.version_id, uuid.UUID)

    def test_version_id_unique_per_version(self):
        identity = KnowledgeIdentity.create()
        v1 = create_version(identity.id, version_number=1)
        v2 = create_version(identity.id, version_number=2)
        assert v1.version_id != v2.version_id

    def test_version_id_frozen(self):
        identity = KnowledgeIdentity.create()
        v = create_version(identity.id)
        with pytest.raises(AttributeError):
            v.version_id = uuid.uuid4()

    def test_version_id_explicit(self):
        identity = KnowledgeIdentity.create()
        explicit_id = uuid.uuid4()
        v = KnowledgeVersion(
            identity_id=identity.id,
            version_id=explicit_id,
            version_number=1,
            knowledge_type=KnowledgeType.DECISION,
            title="Test",
            understanding="Test",
            confidence=0.8,
            lifecycle_state=LifecycleState.DRAFT,
            evidence=(),
            relationships=(),
            created_at=datetime.now(timezone.utc),
        )
        assert v.version_id == explicit_id


class TestKnowledgeVersionOrdering:
    def test_version_number_ordering(self):
        identity = KnowledgeIdentity.create()
        v1 = create_version(identity.id, version_number=1)
        v2 = create_version(identity.id, version_number=2)
        v3 = create_version(identity.id, version_number=3)

        assert v1.version_number < v2.version_number < v3.version_number

    def test_versions_can_be_sorted(self):
        identity = KnowledgeIdentity.create()
        versions = [
            create_version(identity.id, version_number=3),
            create_version(identity.id, version_number=1),
            create_version(identity.id, version_number=2),
        ]
        sorted_versions = sorted(versions, key=lambda v: v.version_number)
        assert [v.version_number for v in sorted_versions] == [1, 2, 3]


class TestKnowledgeVersionValidation:
    def test_confidence_out_of_range_raises(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(ValueError):
            create_version(identity.id, confidence=1.5)

    def test_negative_confidence_raises(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(ValueError):
            create_version(identity.id, confidence=-0.1)

    def test_version_number_zero_raises(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(ValueError):
            create_version(identity.id, version_number=0)

    def test_negative_version_number_raises(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(ValueError):
            create_version(identity.id, version_number=-1)
