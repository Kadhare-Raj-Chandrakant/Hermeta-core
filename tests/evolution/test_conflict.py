import uuid
from datetime import datetime, timezone

import pytest
from brain.evolution.conflict import Conflict, ConflictStatus


def make_conflict(**kwargs) -> Conflict:
    defaults = dict(
        version_ids=(uuid.uuid4(), uuid.uuid4()),
        description="Test conflict",
    )
    defaults.update(kwargs)
    return Conflict(**defaults)


class TestConflictCreation:
    def test_create_valid(self):
        c = make_conflict()
        assert isinstance(c.id, uuid.UUID)
        assert len(c.version_ids) == 2
        assert c.description == "Test conflict"
        assert c.status == ConflictStatus.OPEN
        assert c.resolution is None
        assert isinstance(c.created_at, datetime)
        assert c.resolved_at is None

    def test_create_with_three_versions(self):
        vids = (uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
        c = make_conflict(version_ids=vids)
        assert len(c.version_ids) == 3


class TestConflictImmutability:
    def test_frozen(self):
        c = make_conflict()
        with pytest.raises(AttributeError):
            c.description = "changed"

    def test_status_frozen(self):
        c = make_conflict()
        with pytest.raises(AttributeError):
            c.status = ConflictStatus.RESOLVED

    def test_version_ids_frozen(self):
        c = make_conflict()
        with pytest.raises(AttributeError):
            c.version_ids = (uuid.uuid4(),)


class TestConflictValidation:
    def test_single_version_raises(self):
        with pytest.raises(ValueError, match="at least two"):
            make_conflict(version_ids=(uuid.uuid4(),))

    def test_empty_version_ids_raises(self):
        with pytest.raises(ValueError, match="at least two"):
            make_conflict(version_ids=())

    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_conflict(description="")

    def test_whitespace_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_conflict(description="  ")


class TestConflictStatus:
    def test_open_value(self):
        assert ConflictStatus.OPEN.value == "open"

    def test_resolved_value(self):
        assert ConflictStatus.RESOLVED.value == "resolved"

    def test_two_values(self):
        assert len(ConflictStatus) == 2
