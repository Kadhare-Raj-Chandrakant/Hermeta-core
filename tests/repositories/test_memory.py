import uuid
import pytest
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.identity import KnowledgeIdentity
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion
from brain.repositories.memory import (
    DuplicateVersionError,
    IdentityNotFoundError,
    InMemoryKnowledgeRepository,
    VersionNotFoundError,
)


def make_version(
    identity_id,
    version_number: int = 1,
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id,
        version_number=version_number,
        knowledge_type=knowledge_type,
        title=f"Title {version_number}",
        understanding=f"Understanding {version_number}",
        confidence=0.8,
        lifecycle_state=LifecycleState.DRAFT,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestIdentityCreation:
    def test_create_identity_returns_identity(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        assert isinstance(identity, KnowledgeIdentity)

    def test_create_identity_returns_unique_ids(self):
        repo = InMemoryKnowledgeRepository()
        i1 = repo.create_identity()
        i2 = repo.create_identity()
        assert i1.id != i2.id

    def test_get_identity_after_creation(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        retrieved = repo.get_identity(identity.id)
        assert retrieved == identity


class TestVersionInsertion:
    def test_add_version(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        version = make_version(identity.id, version_number=1)
        repo.add_version(version)
        retrieved = repo.get_version(identity.id, 1)
        assert retrieved == version

    def test_add_multiple_versions(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        v2 = make_version(identity.id, version_number=2)
        v3 = make_version(identity.id, version_number=3)
        repo.add_version(v1)
        repo.add_version(v2)
        repo.add_version(v3)
        assert len(repo.list_versions(identity.id)) == 3


class TestDuplicateRejection:
    def test_duplicate_version_number_raises(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        v2 = make_version(identity.id, version_number=1)
        repo.add_version(v1)
        with pytest.raises(DuplicateVersionError) as exc_info:
            repo.add_version(v2)
        assert exc_info.value.identity_id == identity.id
        assert exc_info.value.version_number == 1

    def test_different_identities_same_version_ok(self):
        repo = InMemoryKnowledgeRepository()
        i1 = repo.create_identity()
        i2 = repo.create_identity()
        v1 = make_version(i1.id, version_number=1)
        v2 = make_version(i2.id, version_number=1)
        repo.add_version(v1)
        repo.add_version(v2)
        assert repo.get_version(i1.id, 1) == v1
        assert repo.get_version(i2.id, 1) == v2


class TestLatestVersionRetrieval:
    def test_latest_version_single(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        repo.add_version(v1)
        assert repo.get_latest_version(identity.id) == v1

    def test_latest_version_multiple(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        v2 = make_version(identity.id, version_number=2)
        v3 = make_version(identity.id, version_number=3)
        repo.add_version(v1)
        repo.add_version(v2)
        repo.add_version(v3)
        assert repo.get_latest_version(identity.id) == v3

    def test_latest_version_out_of_order_insertion(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v3 = make_version(identity.id, version_number=3)
        v1 = make_version(identity.id, version_number=1)
        repo.add_version(v3)
        repo.add_version(v1)
        assert repo.get_latest_version(identity.id) == v3


class TestHistoryRetrieval:
    def test_list_versions_empty(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        assert repo.list_versions(identity.id) == ()

    def test_list_versions_ordered(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v3 = make_version(identity.id, version_number=3)
        v1 = make_version(identity.id, version_number=1)
        v2 = make_version(identity.id, version_number=2)
        repo.add_version(v3)
        repo.add_version(v1)
        repo.add_version(v2)
        versions = repo.list_versions(identity.id)
        assert [v.version_number for v in versions] == [1, 2, 3]

    def test_list_versions_returns_tuple(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        repo.add_version(v1)
        result = repo.list_versions(identity.id)
        assert isinstance(result, tuple)


class TestUnknownIdentityHandling:
    def test_get_identity_unknown_raises(self):
        repo = InMemoryKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_identity(DeterministicUUID.one())

    def test_get_latest_version_unknown_identity_raises(self):
        repo = InMemoryKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_latest_version(DeterministicUUID.one())

    def test_get_version_unknown_identity_raises(self):
        repo = InMemoryKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_version(DeterministicUUID.one(), 1)

    def test_list_versions_unknown_identity_raises(self):
        repo = InMemoryKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.list_versions(DeterministicUUID.one())

    def test_add_version_unknown_identity_raises(self):
        repo = InMemoryKnowledgeRepository()
        version = make_version(DeterministicUUID.one(), version_number=1)
        with pytest.raises(IdentityNotFoundError):
            repo.add_version(version)


class TestNoVersionHistory:
    def test_get_latest_version_no_versions_raises(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        with pytest.raises(VersionNotFoundError):
            repo.get_latest_version(identity.id)

    def test_get_version_not_found_raises(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        with pytest.raises(VersionNotFoundError):
            repo.get_version(identity.id, 1)


class TestImmutabilityPreserved:
    def test_stored_version_not_mutated(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        repo.add_version(v1)
        retrieved = repo.get_version(identity.id, 1)
        assert retrieved is v1


class DeterministicUUID:
    @classmethod
    def one(cls) -> uuid.UUID:
        return uuid.UUID("00000000-0000-0000-0000-000000000001")
