import pytest
from datetime import datetime, timezone
import uuid

from brain.domain.identity import KnowledgeIdentity


class TestKnowledgeIdentityImmutability:
    def test_identity_is_frozen(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(AttributeError):
            identity.id = uuid.uuid4()

    def test_identity_created_at_is_frozen(self):
        identity = KnowledgeIdentity.create()
        with pytest.raises(AttributeError):
            identity.created_at = datetime.now(timezone.utc)

    def test_identity_equality(self):
        id_val = uuid.uuid4()
        now = datetime.now(timezone.utc)
        identity1 = KnowledgeIdentity(id=id_val, created_at=now)
        identity2 = KnowledgeIdentity(id=id_val, created_at=now)
        assert identity1 == identity2

    def test_identity_inequality(self):
        identity1 = KnowledgeIdentity.create()
        identity2 = KnowledgeIdentity.create()
        assert identity1 != identity2


class TestKnowledgeIdentityCreation:
    def test_create_generates_uuid(self):
        identity = KnowledgeIdentity.create()
        assert isinstance(identity.id, uuid.UUID)

    def test_create_sets_timestamp(self):
        identity = KnowledgeIdentity.create()
        assert isinstance(identity.created_at, datetime)

    def test_create_generates_unique_ids(self):
        identity1 = KnowledgeIdentity.create()
        identity2 = KnowledgeIdentity.create()
        assert identity1.id != identity2.id
