from abc import ABC, abstractmethod
import uuid

from brain.domain.identity import KnowledgeIdentity
from brain.domain.version import KnowledgeVersion


class KnowledgeRepository(ABC):
    @abstractmethod
    def create_identity(self) -> KnowledgeIdentity:
        """Create and store a new KnowledgeIdentity."""

    @abstractmethod
    def add_version(self, version: KnowledgeVersion) -> None:
        """Store a KnowledgeVersion. Rejects duplicate version numbers for the same identity."""

    @abstractmethod
    def get_identity(self, identity_id: uuid.UUID) -> KnowledgeIdentity:
        """Retrieve a KnowledgeIdentity by ID. Raises KeyError if not found."""

    @abstractmethod
    def get_latest_version(self, identity_id: uuid.UUID) -> KnowledgeVersion:
        """Retrieve the latest version for an identity. Raises KeyError if none found."""

    @abstractmethod
    def get_version(self, identity_id: uuid.UUID, version_number: int) -> KnowledgeVersion:
        """Retrieve a specific version. Raises KeyError if not found."""

    @abstractmethod
    def list_versions(self, identity_id: uuid.UUID) -> tuple[KnowledgeVersion, ...]:
        """Return all versions for an identity, ordered by version number."""

    @abstractmethod
    def list_all_versions(self) -> tuple[KnowledgeVersion, ...]:
        """Return all versions across all identities."""
