import uuid
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.identity import KnowledgeIdentity
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion
from brain.evolution.conflict import Conflict, ConflictStatus
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.infrastructure.sqlite.connection import SQLiteConnection
from brain.infrastructure.sqlite.schema import initialize_schema
from brain.repositories.base import KnowledgeRepository
from brain.repositories.evolution_base import EvolutionRepository
from brain.repositories.memory import (
    DuplicateVersionError,
    IdentityNotFoundError,
    VersionNotFoundError,
)


class SQLiteKnowledgeRepository(KnowledgeRepository, EvolutionRepository):
    def __init__(self, db_path: str | None = None) -> None:
        self._conn = SQLiteConnection(db_path or ":memory:")
        initialize_schema(self._conn)

    def create_identity(self) -> KnowledgeIdentity:
        identity = KnowledgeIdentity.create()
        self._conn.execute(
            "INSERT INTO identities (id, created_at) VALUES (?, ?)",
            (str(identity.id), identity.created_at.isoformat()),
        )
        self._conn.commit()
        return identity

    def add_version(self, version: KnowledgeVersion) -> None:
        row = self._conn.execute(
            "SELECT id FROM identities WHERE id = ?",
            (str(version.identity_id),),
        ).fetchone()
        if row is None:
            raise IdentityNotFoundError(version.identity_id)

        existing = self._conn.execute(
            "SELECT version_number FROM versions WHERE identity_id = ? AND version_number = ?",
            (str(version.identity_id), version.version_number),
        ).fetchone()
        if existing is not None:
            raise DuplicateVersionError(version.identity_id, version.version_number)

        self._conn.execute(
            """INSERT INTO versions
            (identity_id, version_id, version_number, knowledge_type, title, understanding,
             confidence, lifecycle_state, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(version.identity_id),
                str(version.version_id),
                version.version_number,
                version.knowledge_type.value,
                version.title,
                version.understanding,
                version.confidence,
                version.lifecycle_state.value,
                version.created_at.isoformat(),
            ),
        )

        for ev in version.evidence:
            self._conn.execute(
                "INSERT INTO evidence (identity_id, version_number, source, reference) VALUES (?, ?, ?, ?)",
                (str(version.identity_id), version.version_number, ev.source, ev.reference),
            )

        for rel in version.relationships:
            self._conn.execute(
                "INSERT INTO relationships (identity_id, version_number, target_id, relationship_type) VALUES (?, ?, ?, ?)",
                (str(version.identity_id), version.version_number, str(rel.target_id), rel.relationship_type),
            )

        self._conn.commit()

    def get_identity(self, identity_id: uuid.UUID) -> KnowledgeIdentity:
        row = self._conn.execute(
            "SELECT id, created_at FROM identities WHERE id = ?",
            (str(identity_id),),
        ).fetchone()
        if row is None:
            raise IdentityNotFoundError(identity_id)
        return KnowledgeIdentity(
            id=uuid.UUID(row["id"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_latest_version(self, identity_id: uuid.UUID) -> KnowledgeVersion:
        row = self._conn.execute(
            "SELECT id FROM identities WHERE id = ?",
            (str(identity_id),),
        ).fetchone()
        if row is None:
            raise IdentityNotFoundError(identity_id)

        row = self._conn.execute(
            "SELECT version_number FROM versions WHERE identity_id = ? ORDER BY version_number DESC LIMIT 1",
            (str(identity_id),),
        ).fetchone()
        if row is None:
            raise VersionNotFoundError(identity_id, -1)

        return self._load_version(identity_id, row["version_number"])

    def get_version(self, identity_id: uuid.UUID, version_number: int) -> KnowledgeVersion:
        row = self._conn.execute(
            "SELECT id FROM identities WHERE id = ?",
            (str(identity_id),),
        ).fetchone()
        if row is None:
            raise IdentityNotFoundError(identity_id)

        row = self._conn.execute(
            "SELECT version_number FROM versions WHERE identity_id = ? AND version_number = ?",
            (str(identity_id), version_number),
        ).fetchone()
        if row is None:
            raise VersionNotFoundError(identity_id, version_number)

        return self._load_version(identity_id, version_number)

    def list_versions(self, identity_id: uuid.UUID) -> tuple[KnowledgeVersion, ...]:
        row = self._conn.execute(
            "SELECT id FROM identities WHERE id = ?",
            (str(identity_id),),
        ).fetchone()
        if row is None:
            raise IdentityNotFoundError(identity_id)

        rows = self._conn.execute(
            "SELECT version_number FROM versions WHERE identity_id = ? ORDER BY version_number",
            (str(identity_id),),
        ).fetchall()
        return tuple(self._load_version(identity_id, r["version_number"]) for r in rows)

    def list_all_versions(self) -> tuple[KnowledgeVersion, ...]:
        rows = self._conn.execute(
            "SELECT identity_id, version_number FROM versions ORDER BY version_number"
        ).fetchall()
        return tuple(
            self._load_version(uuid.UUID(r["identity_id"]), r["version_number"]) for r in rows
        )

    def _load_version(self, identity_id: uuid.UUID, version_number: int) -> KnowledgeVersion:
        row = self._conn.execute(
            """SELECT version_id, knowledge_type, title, understanding, confidence,
                      lifecycle_state, created_at
            FROM versions WHERE identity_id = ? AND version_number = ?""",
            (str(identity_id), version_number),
        ).fetchone()

        evidence_rows = self._conn.execute(
            "SELECT source, reference FROM evidence WHERE identity_id = ? AND version_number = ?",
            (str(identity_id), version_number),
        ).fetchall()

        relationship_rows = self._conn.execute(
            "SELECT target_id, relationship_type FROM relationships WHERE identity_id = ? AND version_number = ?",
            (str(identity_id), version_number),
        ).fetchall()

        return KnowledgeVersion(
            identity_id=identity_id,
            version_id=uuid.UUID(row["version_id"]),
            version_number=version_number,
            knowledge_type=KnowledgeType(row["knowledge_type"]),
            title=row["title"],
            understanding=row["understanding"],
            confidence=row["confidence"],
            lifecycle_state=LifecycleState(row["lifecycle_state"]),
            evidence=tuple(Evidence(source=r["source"], reference=r["reference"]) for r in evidence_rows),
            relationships=tuple(
                Relationship(target_id=uuid.UUID(r["target_id"]), relationship_type=r["relationship_type"])
                for r in relationship_rows
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def create_transition(self, transition: KnowledgeTransition) -> None:
        self._conn.execute(
            """INSERT INTO transitions
            (id, from_version_id, to_version_id, transition_type, reason, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(transition.id),
                str(transition.from_version_id),
                str(transition.to_version_id),
                transition.transition_type.value,
                transition.reason,
                transition.confidence,
                transition.source,
                transition.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def get_transitions_for_version(self, version_id: uuid.UUID) -> tuple[KnowledgeTransition, ...]:
        vid = str(version_id)
        rows = self._conn.execute(
            """SELECT id, from_version_id, to_version_id, transition_type,
                      reason, confidence, source, created_at
            FROM transitions
            WHERE from_version_id = ? OR to_version_id = ?""",
            (vid, vid),
        ).fetchall()
        return tuple(self._load_transition(r) for r in rows)

    def get_all_transitions(self) -> tuple[KnowledgeTransition, ...]:
        rows = self._conn.execute(
            """SELECT id, from_version_id, to_version_id, transition_type,
                      reason, confidence, source, created_at
            FROM transitions"""
        ).fetchall()
        return tuple(self._load_transition(r) for r in rows)

    def _load_transition(self, row: object) -> KnowledgeTransition:
        return KnowledgeTransition(
            id=uuid.UUID(row["id"]),
            from_version_id=uuid.UUID(row["from_version_id"]),
            to_version_id=uuid.UUID(row["to_version_id"]),
            transition_type=TransitionType(row["transition_type"]),
            reason=row["reason"],
            confidence=row["confidence"],
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def create_conflict(self, conflict: Conflict) -> None:
        self._conn.execute(
            """INSERT INTO conflicts
            (id, description, status, resolution, created_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(conflict.id),
                conflict.description,
                conflict.status.value,
                conflict.resolution,
                conflict.created_at.isoformat(),
                conflict.resolved_at.isoformat() if conflict.resolved_at else None,
            ),
        )
        for vid in conflict.version_ids:
            self._conn.execute(
                "INSERT INTO conflict_versions (conflict_id, version_id) VALUES (?, ?)",
                (str(conflict.id), str(vid)),
            )
        self._conn.commit()

    def get_conflicts(self) -> tuple[Conflict, ...]:
        rows = self._conn.execute(
            "SELECT id, description, status, resolution, created_at, resolved_at FROM conflicts"
        ).fetchall()
        return tuple(self._load_conflict(r) for r in rows)

    def _load_conflict(self, row: object) -> Conflict:
        conflict_id = row["id"]
        vid_rows = self._conn.execute(
            "SELECT version_id FROM conflict_versions WHERE conflict_id = ?",
            (conflict_id,),
        ).fetchall()
        return Conflict(
            id=uuid.UUID(conflict_id),
            version_ids=tuple(uuid.UUID(r["version_id"]) for r in vid_rows),
            description=row["description"],
            status=ConflictStatus(row["status"]),
            resolution=row["resolution"],
            created_at=datetime.fromisoformat(row["created_at"]),
            resolved_at=datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None,
        )
