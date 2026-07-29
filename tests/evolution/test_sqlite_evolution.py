import uuid
from datetime import datetime, timezone

import pytest
from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.version import KnowledgeVersion
from brain.evolution.conflict import Conflict, ConflictStatus
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.infrastructure.sqlite.repository import SQLiteKnowledgeRepository


def make_version(
    identity_id: uuid.UUID | None = None,
    version_number: int = 1,
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id or uuid.uuid4(),
        version_number=version_number,
        knowledge_type=KnowledgeType.DECISION,
        title="Test Knowledge",
        understanding="Test understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def repo() -> SQLiteKnowledgeRepository:
    return SQLiteKnowledgeRepository(":memory:")


class TestSQLiteTransitionStorage:
    def test_create_and_retrieve_transition(self, repo: SQLiteKnowledgeRepository):
        fid = uuid.uuid4()
        tid = uuid.uuid4()
        t = KnowledgeTransition(
            from_version_id=fid,
            to_version_id=tid,
            transition_type=TransitionType.UPDATE,
            reason="Test",
            confidence=0.9,
            source="test",
        )
        repo.create_transition(t)

        result = repo.get_transitions_for_version(fid)
        assert len(result) == 1
        assert result[0].transition_type == TransitionType.UPDATE

    def test_get_transitions_by_to_version(self, repo: SQLiteKnowledgeRepository):
        fid = uuid.uuid4()
        tid = uuid.uuid4()
        t = KnowledgeTransition(
            from_version_id=fid,
            to_version_id=tid,
            transition_type=TransitionType.SUPERSEDES,
            reason="Replaced",
            confidence=0.8,
            source="manual",
        )
        repo.create_transition(t)

        result = repo.get_transitions_for_version(tid)
        assert len(result) == 1

    def test_multiple_transitions(self, repo: SQLiteKnowledgeRepository):
        vid = uuid.uuid4()
        t1 = KnowledgeTransition(
            from_version_id=vid, to_version_id=uuid.uuid4(),
            transition_type=TransitionType.UPDATE, reason="A", confidence=1.0, source="s",
        )
        t2 = KnowledgeTransition(
            from_version_id=uuid.uuid4(), to_version_id=vid,
            transition_type=TransitionType.EXTENDS, reason="B", confidence=0.7, source="s",
        )
        repo.create_transition(t1)
        repo.create_transition(t2)

        result = repo.get_transitions_for_version(vid)
        assert len(result) == 2

    def test_get_all_transitions(self, repo: SQLiteKnowledgeRepository):
        t1 = KnowledgeTransition(
            from_version_id=uuid.uuid4(), to_version_id=uuid.uuid4(),
            transition_type=TransitionType.UPDATE, reason="A", confidence=1.0, source="s",
        )
        repo.create_transition(t1)

        result = repo.get_all_transitions()
        assert len(result) == 1

    def test_transition_preserves_all_fields(self, repo: SQLiteKnowledgeRepository):
        fid = uuid.uuid4()
        tid = uuid.uuid4()
        ts = datetime(2025, 6, 15, tzinfo=timezone.utc)
        t = KnowledgeTransition(
            id=uuid.UUID(int=42),
            from_version_id=fid,
            to_version_id=tid,
            transition_type=TransitionType.REFINEMENT,
            reason="More specific",
            confidence=0.85,
            source="review",
            created_at=ts,
        )
        repo.create_transition(t)

        result = repo.get_transitions_for_version(fid)[0]
        assert result.id == uuid.UUID(int=42)
        assert result.from_version_id == fid
        assert result.to_version_id == tid
        assert result.transition_type == TransitionType.REFINEMENT
        assert result.reason == "More specific"
        assert result.confidence == 0.85
        assert result.source == "review"
        assert result.created_at == ts


class TestSQLiteConflictStorage:
    def test_create_and_retrieve_conflict(self, repo: SQLiteKnowledgeRepository):
        vid1 = uuid.uuid4()
        vid2 = uuid.uuid4()
        c = Conflict(
            version_ids=(vid1, vid2),
            description="Incompatible",
        )
        repo.create_conflict(c)

        result = repo.get_conflicts()
        assert len(result) == 1
        assert result[0].description == "Incompatible"
        assert set(result[0].version_ids) == {vid1, vid2}

    def test_conflict_status_preserved(self, repo: SQLiteKnowledgeRepository):
        c = Conflict(
            version_ids=(uuid.uuid4(), uuid.uuid4()),
            description="Test",
            status=ConflictStatus.OPEN,
        )
        repo.create_conflict(c)

        result = repo.get_conflicts()[0]
        assert result.status == ConflictStatus.OPEN

    def test_multiple_conflicts(self, repo: SQLiteKnowledgeRepository):
        c1 = Conflict(version_ids=(uuid.uuid4(), uuid.uuid4()), description="A")
        c2 = Conflict(version_ids=(uuid.uuid4(), uuid.uuid4()), description="B")
        repo.create_conflict(c1)
        repo.create_conflict(c2)

        result = repo.get_conflicts()
        assert len(result) == 2

    def test_conflict_with_three_versions(self, repo: SQLiteKnowledgeRepository):
        vids = (uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
        c = Conflict(version_ids=vids, description="Three-way")
        repo.create_conflict(c)

        result = repo.get_conflicts()[0]
        assert len(result.version_ids) == 3
        assert set(result.version_ids) == set(vids)


class TestSQLiteSchemaVersion:
    def test_schema_version_is_3(self, repo: SQLiteKnowledgeRepository):
        row = repo._conn.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1").fetchone()
        assert row["version"] == 3


class TestSQLiteExistingBehaviorPreserved:
    def test_create_identity_still_works(self, repo: SQLiteKnowledgeRepository):
        identity = repo.create_identity()
        assert identity.id is not None

    def test_add_version_still_works(self, repo: SQLiteKnowledgeRepository):
        identity = repo.create_identity()
        v = make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v)
        latest = repo.get_latest_version(identity.id)
        assert latest.version_number == 1

    def test_list_versions_still_works(self, repo: SQLiteKnowledgeRepository):
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)
        versions = repo.list_versions(identity.id)
        assert len(versions) == 2


class TestSQLiteVersionIdPersistence:
    def test_version_id_persisted(self, repo: SQLiteKnowledgeRepository):
        identity = repo.create_identity()
        v = make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v)
        loaded = repo.get_latest_version(identity.id)
        assert loaded.version_id == v.version_id

    def test_version_id_unique_across_versions(self, repo: SQLiteKnowledgeRepository):
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)
        loaded1 = repo.get_version(identity.id, 1)
        loaded2 = repo.get_version(identity.id, 2)
        assert loaded1.version_id != loaded2.version_id
