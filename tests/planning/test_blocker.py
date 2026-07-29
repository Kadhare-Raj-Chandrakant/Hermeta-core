import uuid

import pytest

from brain.planning.blocker import Blocker, BlockerSeverity


def make_blocker(**kwargs) -> Blocker:
    defaults = dict(
        action_id=uuid.uuid4(),
        description="Test blocker description",
        severity=BlockerSeverity.MEDIUM,
    )
    defaults.update(kwargs)
    return Blocker(**defaults)


class TestBlockerCreation:
    def test_create_valid(self):
        b = make_blocker()
        assert isinstance(b.id, uuid.UUID)
        assert isinstance(b.action_id, uuid.UUID)
        assert b.description == "Test blocker description"
        assert b.severity == BlockerSeverity.MEDIUM


class TestBlockerImmutability:
    def test_frozen(self):
        b = make_blocker()
        with pytest.raises(AttributeError):
            b.description = "changed"

    def test_severity_frozen(self):
        b = make_blocker()
        with pytest.raises(AttributeError):
            b.severity = BlockerSeverity.CRITICAL


class TestBlockerValidation:
    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_blocker(description="")

    def test_whitespace_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_blocker(description="  ")


class TestBlockerSeverity:
    def test_four_values(self):
        assert len(BlockerSeverity) == 4

    def test_values(self):
        assert BlockerSeverity.LOW.value == "low"
        assert BlockerSeverity.MEDIUM.value == "medium"
        assert BlockerSeverity.HIGH.value == "high"
        assert BlockerSeverity.CRITICAL.value == "critical"
