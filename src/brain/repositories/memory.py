import uuid
import threading

from brain.domain.identity import KnowledgeIdentity
from brain.domain.version import KnowledgeVersion
from brain.evolution.conflict import Conflict
from brain.evolution.transition import KnowledgeTransition
from brain.repositories.base import KnowledgeRepository
from brain.repositories.evolution_base import EvolutionRepository


class DuplicateVersionError(Exception):
    def __init__(self, identity_id: uuid.UUID, version_number: int) -> None:
        self.identity_id = identity_id
        self.version_number = version_number
        super().__init__(f"Version {version_number} already exists for identity {identity_id}")


class IdentityNotFoundError(Exception):
    def __init__(self, identity_id: uuid.UUID) -> None:
        self.identity_id = identity_id
        super().__init__(f"Identity {identity_id} not found")


class VersionNotFoundError(Exception):
    def __init__(self, identity_id: uuid.UUID, version_number: int) -> None:
        self.identity_id = identity_id
        self.version_number = version_number
        super().__init__(f"Version {version_number} not found for identity {identity_id}")


class InMemoryKnowledgeRepository(KnowledgeRepository, EvolutionRepository):
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._identities: dict[uuid.UUID, KnowledgeIdentity] = {}
        self._versions: dict[uuid.UUID, list[KnowledgeVersion]] = {}
        self._transitions: list[KnowledgeTransition] = []
        self._conflicts: list[Conflict] = []
        self._execution_records: list[object] = []

    def snapshot(self):
        with self._lock:
            return (
                dict(self._identities),
                {k: list(v) for k, v in self._versions.items()},
                list(self._transitions),
                list(self._conflicts),
                list(self._execution_records),
            )

    def restore(self, snapshot) -> None:
        with self._lock:
            self._identities, self._versions, self._transitions, self._conflicts, self._execution_records = snapshot

    def create_identity(self) -> KnowledgeIdentity:
        with self._lock:
            identity = KnowledgeIdentity.create()
            self._identities[identity.id] = identity
            self._versions[identity.id] = []
            return identity

    def add_version(self, version: KnowledgeVersion) -> None:
        with self._lock:
            if version.identity_id not in self._identities:
                raise IdentityNotFoundError(version.identity_id)

            versions = self._versions[version.identity_id]
            for existing in versions:
                if existing.version_number == version.version_number:
                    raise DuplicateVersionError(version.identity_id, version.version_number)

            versions.append(version)

    def get_identity(self, identity_id: uuid.UUID) -> KnowledgeIdentity:
        with self._lock:
            if identity_id not in self._identities:
                raise IdentityNotFoundError(identity_id)
            return self._identities[identity_id]

    def get_latest_version(self, identity_id: uuid.UUID) -> KnowledgeVersion:
        with self._lock:
            if identity_id not in self._identities:
                raise IdentityNotFoundError(identity_id)

            versions = self._versions[identity_id]
            if not versions:
                raise VersionNotFoundError(identity_id, -1)

            return max(versions, key=lambda v: v.version_number)

    def get_version(self, identity_id: uuid.UUID, version_number: int) -> KnowledgeVersion:
        with self._lock:
            if identity_id not in self._identities:
                raise IdentityNotFoundError(identity_id)

            for version in self._versions[identity_id]:
                if version.version_number == version_number:
                    return version

            raise VersionNotFoundError(identity_id, version_number)

    def list_versions(self, identity_id: uuid.UUID) -> tuple[KnowledgeVersion, ...]:
        with self._lock:
            if identity_id not in self._identities:
                raise IdentityNotFoundError(identity_id)

            versions = sorted(self._versions[identity_id], key=lambda v: v.version_number)
            return tuple(versions)

    def list_all_versions(self) -> tuple[KnowledgeVersion, ...]:
        with self._lock:
            all_versions = []
            for versions in self._versions.values():
                all_versions.extend(versions)
            return tuple(sorted(all_versions, key=lambda v: v.version_number))

    def replace_version(self, version: KnowledgeVersion) -> None:
        with self._lock:
            identity_versions = self._versions.get(version.identity_id)
            if identity_versions is None:
                raise IdentityNotFoundError(version.identity_id)
            for i, existing in enumerate(identity_versions):
                if existing.version_id == version.version_id:
                    identity_versions[i] = version
                    return
            raise VersionNotFoundError(version.identity_id, version.version_number)

    def create_transition(self, transition: KnowledgeTransition) -> None:
        with self._lock:
            self._transitions.append(transition)

    def get_transitions_for_version(self, version_id: uuid.UUID) -> tuple[KnowledgeTransition, ...]:
        with self._lock:
            return tuple(
                t for t in self._transitions
                if t.from_version_id == version_id or t.to_version_id == version_id
            )

    def get_all_transitions(self) -> tuple[KnowledgeTransition, ...]:
        with self._lock:
            return tuple(self._transitions)

    def create_conflict(self, conflict: Conflict) -> None:
        with self._lock:
            self._conflicts.append(conflict)

    def get_conflicts(self) -> tuple[Conflict, ...]:
        with self._lock:
            return tuple(self._conflicts)

    def save_execution_record(self, record: object) -> None:
        with self._lock:
            self._execution_records.append(record)

    def get_execution_records(self) -> tuple[object, ...]:
        with self._lock:
            return tuple(self._execution_records)
