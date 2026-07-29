import uuid
from datetime import datetime, timezone

import pytest
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType


def make_transition(**kwargs) -> KnowledgeTransition:
    defaults = dict(
        from_version_id=uuid.uuid4(),
        to_version_id=uuid.uuid4(),
        transition_type=TransitionType.UPDATE,
        reason="Test reason",
        confidence=0.9,
        source="test",
    )
    defaults.update(kwargs)
    return KnowledgeTransition(**defaults)


class TestTransitionCreation:
    def test_create_valid(self):
        t = make_transition()
        assert isinstance(t.id, uuid.UUID)
        assert t.transition_type == TransitionType.UPDATE
        assert t.reason == "Test reason"
        assert t.confidence == 0.9
        assert t.source == "test"
        assert isinstance(t.created_at, datetime)

    def test_create_with_explicit_fields(self):
        fid = uuid.uuid4()
        tid = uuid.uuid4()
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        t = KnowledgeTransition(
            from_version_id=fid,
            to_version_id=tid,
            transition_type=TransitionType.SUPERSEDES,
            reason="Old replaced",
            confidence=0.8,
            source="manual",
            id=uuid.UUID(int=0),
            created_at=ts,
        )
        assert t.id == uuid.UUID(int=0)
        assert t.from_version_id == fid
        assert t.to_version_id == tid
        assert t.created_at == ts


class TestTransitionImmutability:
    def test_frozen(self):
        t = make_transition()
        with pytest.raises(AttributeError):
            t.reason = "changed"

    def test_id_frozen(self):
        t = make_transition()
        with pytest.raises(AttributeError):
            t.id = uuid.uuid4()

    def test_from_version_id_frozen(self):
        t = make_transition()
        with pytest.raises(AttributeError):
            t.from_version_id = uuid.uuid4()


class TestTransitionValidation:
    def test_confidence_above_one_raises(self):
        with pytest.raises(ValueError, match="Confidence must be between"):
            make_transition(confidence=1.5)

    def test_confidence_negative_raises(self):
        with pytest.raises(ValueError, match="Confidence must be between"):
            make_transition(confidence=-0.1)

    def test_empty_reason_raises(self):
        with pytest.raises(ValueError, match="reason must not be empty"):
            make_transition(reason="")

    def test_whitespace_reason_raises(self):
        with pytest.raises(ValueError, match="reason must not be empty"):
            make_transition(reason="   ")

    def test_empty_source_raises(self):
        with pytest.raises(ValueError, match="source must not be empty"):
            make_transition(source="")

    def test_whitespace_source_raises(self):
        with pytest.raises(ValueError, match="source must not be empty"):
            make_transition(source="  ")

    def test_same_version_ids_allowed(self):
        fid = uuid.uuid4()
        t = make_transition(from_version_id=fid, to_version_id=fid)
        assert t.from_version_id == fid
        assert t.to_version_id == fid

    def test_boundary_confidence_zero_passes(self):
        t = make_transition(confidence=0.0)
        assert t.confidence == 0.0

    def test_boundary_confidence_one_passes(self):
        t = make_transition(confidence=1.0)
        assert t.confidence == 1.0
