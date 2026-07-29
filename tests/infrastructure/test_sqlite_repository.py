import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion
from brain.infrastructure.sqlite.repository import SQLiteKnowledgeRepository
from brain.repositories.memory import (
    DuplicateVersionError,
    IdentityNotFoundError,
    InMemoryKnowledgeRepository,
    VersionNotFoundError,
)


def make_version(
    identity_id: uuid.UUID,
    version_number: int = 1,
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test",
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id,
        version_number=version_number,
        knowledge_type=knowledge_type,
        title=title,
        understanding="Understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(Evidence(source="conversation", reference="test"),),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


class TestIdentityCreation:
    def test_create_identity_returns_identity(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        assert identity.id is not None
        assert identity.created_at is not None

    def test_create_identity_returns_unique_ids(self):
        repo = SQLiteKnowledgeRepository()
        i1 = repo.create_identity()
        i2 = repo.create_identity()
        assert i1.id != i2.id

    def test_get_identity_after_creation(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        retrieved = repo.get_identity(identity.id)
        assert retrieved.id == identity.id
        assert retrieved.created_at == identity.created_at


class TestVersionInsertion:
    def test_add_version(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        version = make_version(identity.id)
        repo.add_version(version)
        latest = repo.get_latest_version(identity.id)
        assert latest.title == "Test"

    def test_add_multiple_versions(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1, title="V1")
        v2 = make_version(identity.id, version_number=2, title="V2")
        repo.add_version(v1)
        repo.add_version(v2)
        latest = repo.get_latest_version(identity.id)
        assert latest.title == "V2"


class TestDuplicateRejection:
    def test_duplicate_version_number_raises(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        v1 = make_version(identity.id, version_number=1)
        v2 = make_version(identity.id, version_number=1)
        repo.add_version(v1)
        with pytest.raises(DuplicateVersionError):
            repo.add_version(v2)

    def test_different_identities_same_version_ok(self):
        repo = SQLiteKnowledgeRepository()
        i1 = repo.create_identity()
        i2 = repo.create_identity()
        v1 = make_version(i1.id, version_number=1)
        v2 = make_version(i2.id, version_number=1)
        repo.add_version(v1)
        repo.add_version(v2)
        assert repo.get_latest_version(i1.id).title == "Test"
        assert repo.get_latest_version(i2.id).title == "Test"


class TestLatestVersionRetrieval:
    def test_latest_version_single(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        v = make_version(identity.id, version_number=1, title="Only")
        repo.add_version(v)
        latest = repo.get_latest_version(identity.id)
        assert latest.title == "Only"

    def test_latest_version_multiple(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        repo.add_version(make_version(identity.id, 1, title="First"))
        repo.add_version(make_version(identity.id, 2, title="Second"))
        repo.add_version(make_version(identity.id, 3, title="Third"))
        latest = repo.get_latest_version(identity.id)
        assert latest.title == "Third"

    def test_latest_version_out_of_order_insertion(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        repo.add_version(make_version(identity.id, 3, title="Third"))
        repo.add_version(make_version(identity.id, 1, title="First"))
        repo.add_version(make_version(identity.id, 2, title="Second"))
        latest = repo.get_latest_version(identity.id)
        assert latest.title == "Third"


class TestHistoryRetrieval:
    def test_list_versions_empty(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        versions = repo.list_versions(identity.id)
        assert versions == ()

    def test_list_versions_ordered(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        repo.add_version(make_version(identity.id, 3, title="C"))
        repo.add_version(make_version(identity.id, 1, title="A"))
        repo.add_version(make_version(identity.id, 2, title="B"))
        versions = repo.list_versions(identity.id)
        assert [v.title for v in versions] == ["A", "B", "C"]

    def test_list_versions_returns_tuple(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        repo.add_version(make_version(identity.id, 1))
        versions = repo.list_versions(identity.id)
        assert isinstance(versions, tuple)


class TestUnknownIdentityHandling:
    def test_get_identity_unknown_raises(self):
        repo = SQLiteKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_identity(uuid.uuid4())

    def test_get_latest_version_unknown_identity_raises(self):
        repo = SQLiteKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_latest_version(uuid.uuid4())

    def test_get_version_unknown_identity_raises(self):
        repo = SQLiteKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.get_version(uuid.uuid4(), 1)

    def test_list_versions_unknown_identity_raises(self):
        repo = SQLiteKnowledgeRepository()
        with pytest.raises(IdentityNotFoundError):
            repo.list_versions(uuid.uuid4())

    def test_add_version_unknown_identity_raises(self):
        repo = SQLiteKnowledgeRepository()
        version = make_version(uuid.uuid4())
        with pytest.raises(IdentityNotFoundError):
            repo.add_version(version)


class TestNoVersionHistory:
    def test_get_latest_version_no_versions_raises(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        with pytest.raises(VersionNotFoundError):
            repo.get_latest_version(identity.id)

    def test_get_version_not_found_raises(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        with pytest.raises(VersionNotFoundError):
            repo.get_version(identity.id, 999)


class TestImmutabilityPreserved:
    def test_stored_version_not_mutated(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        version = make_version(identity.id)
        repo.add_version(version)
        retrieved = repo.get_latest_version(identity.id)
        assert retrieved.title == version.title
        assert retrieved.confidence == version.confidence
        assert retrieved.evidence == version.evidence


class TestListAllVersions:
    def test_list_all_versions_empty(self):
        repo = SQLiteKnowledgeRepository()
        assert repo.list_all_versions() == ()

    def test_list_all_versions_multiple_identities(self):
        repo = SQLiteKnowledgeRepository()
        i1 = repo.create_identity()
        i2 = repo.create_identity()
        repo.add_version(make_version(i1.id, 1, title="A"))
        repo.add_version(make_version(i2.id, 1, title="B"))
        all_versions = repo.list_all_versions()
        assert len(all_versions) == 2


class TestEvidenceAndRelationships:
    def test_evidence_persisted(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        version = KnowledgeVersion(
            identity_id=identity.id,
            version_number=1,
            knowledge_type=KnowledgeType.DECISION,
            title="Test",
            understanding="Test",
            confidence=0.8,
            lifecycle_state=LifecycleState.ACTIVE,
            evidence=(Evidence(source="git", reference="commit abc"),),
            relationships=(),
            created_at=datetime.now(timezone.utc),
        )
        repo.add_version(version)
        retrieved = repo.get_latest_version(identity.id)
        assert len(retrieved.evidence) == 1
        assert retrieved.evidence[0].source == "git"

    def test_relationships_persisted(self):
        repo = SQLiteKnowledgeRepository()
        identity = repo.create_identity()
        target_id = uuid.uuid4()
        version = KnowledgeVersion(
            identity_id=identity.id,
            version_number=1,
            knowledge_type=KnowledgeType.DECISION,
            title="Test",
            understanding="Test",
            confidence=0.8,
            lifecycle_state=LifecycleState.ACTIVE,
            evidence=(),
            relationships=(Relationship(target_id=target_id, relationship_type="depends_on"),),
            created_at=datetime.now(timezone.utc),
        )
        repo.add_version(version)
        retrieved = repo.get_latest_version(identity.id)
        assert len(retrieved.relationships) == 1
        assert retrieved.relationships[0].target_id == target_id


class TestPersistence:
    def test_restart_persistence(self):
        import tempfile
        import os

        db_path = tempfile.mktemp(suffix=".db")
        try:
            repo1 = SQLiteKnowledgeRepository(db_path)
            identity = repo1.create_identity()
            repo1.add_version(make_version(identity.id, 1, title="Persistent"))
            identity_id = identity.id
            repo1._conn.close()

            repo2 = SQLiteKnowledgeRepository(db_path)
            retrieved = repo2.get_latest_version(identity_id)
            assert retrieved.title == "Persistent"
            repo2._conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestBehavioralEquivalence:
    def test_matches_in_memory_behavior(self):
        memory_repo = InMemoryKnowledgeRepository()
        sqlite_repo = SQLiteKnowledgeRepository()

        memory_i1 = memory_repo.create_identity()
        memory_i2 = memory_repo.create_identity()
        sqlite_i1 = sqlite_repo.create_identity()
        sqlite_i2 = sqlite_repo.create_identity()

        memory_repo.add_version(make_version(memory_i1.id, 1, title="First"))
        memory_repo.add_version(make_version(memory_i1.id, 2, title="Second"))
        memory_repo.add_version(make_version(memory_i2.id, 1, title="Only"))

        sqlite_repo.add_version(make_version(sqlite_i1.id, 1, title="First"))
        sqlite_repo.add_version(make_version(sqlite_i1.id, 2, title="Second"))
        sqlite_repo.add_version(make_version(sqlite_i2.id, 1, title="Only"))

        for repo, i1, i2 in [
            (memory_repo, memory_i1, memory_i2),
            (sqlite_repo, sqlite_i1, sqlite_i2),
        ]:
            assert repo.get_latest_version(i1.id).title == "Second"
            assert repo.get_latest_version(i2.id).title == "Only"
            assert len(repo.list_versions(i1.id)) == 2
            assert len(repo.list_all_versions()) == 3
