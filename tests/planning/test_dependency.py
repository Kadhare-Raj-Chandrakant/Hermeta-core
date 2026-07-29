import uuid

import pytest

from brain.planning.dependency import Dependency


def make_dependency(**kwargs) -> Dependency:
    defaults = dict(
        from_action_id=uuid.uuid4(),
        to_action_id=uuid.uuid4(),
        reason="Test dependency reason",
    )
    defaults.update(kwargs)
    return Dependency(**defaults)


class TestDependencyCreation:
    def test_create_valid(self):
        d = make_dependency()
        assert isinstance(d.id, uuid.UUID)
        assert isinstance(d.from_action_id, uuid.UUID)
        assert isinstance(d.to_action_id, uuid.UUID)
        assert d.reason == "Test dependency reason"

    def test_different_ids(self):
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        d = make_dependency(from_action_id=id1, to_action_id=id2)
        assert d.from_action_id == id1
        assert d.to_action_id == id2


class TestDependencyImmutability:
    def test_frozen(self):
        d = make_dependency()
        with pytest.raises(AttributeError):
            d.reason = "changed"

    def test_ids_frozen(self):
        d = make_dependency()
        with pytest.raises(AttributeError):
            d.from_action_id = uuid.uuid4()


class TestDependencyValidation:
    def test_self_dependency_raises(self):
        aid = uuid.uuid4()
        with pytest.raises(ValueError, match="from_action_id cannot equal to_action_id"):
            make_dependency(from_action_id=aid, to_action_id=aid)

    def test_empty_reason_raises(self):
        with pytest.raises(ValueError, match="reason must not be empty"):
            make_dependency(reason="")

    def test_whitespace_reason_raises(self):
        with pytest.raises(ValueError, match="reason must not be empty"):
            make_dependency(reason="  ")
