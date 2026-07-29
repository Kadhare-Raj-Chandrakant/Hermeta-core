import uuid
from datetime import datetime, timezone

import pytest
from brain.evolution.conflict import Conflict, ConflictStatus
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.repositories.memory import InMemoryKnowledgeRepository


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


def make_conflict(**kwargs) -> Conflict:
    defaults = dict(
        version_ids=(uuid.uuid4(), uuid.uuid4()),
        description="Test conflict",
    )
    defaults.update(kwargs)
    return Conflict(**defaults)


class TestInMemoryTransitionStorage:
    def test_create_and_retrieve_transition(self):
        repo = InMemoryKnowledgeRepository()
        t = make_transition()
        repo.create_transition(t)

        result = repo.get_transitions_for_version(t.from_version_id)
        assert len(result) == 1
        assert result[0].id == t.id

    def test_get_transitions_by_to_version(self):
        repo = InMemoryKnowledgeRepository()
        t = make_transition()
        repo.create_transition(t)

        result = repo.get_transitions_for_version(t.to_version_id)
        assert len(result) == 1

    def test_get_transitions_empty(self):
        repo = InMemoryKnowledgeRepository()
        result = repo.get_transitions_for_version(uuid.uuid4())
        assert result == ()

    def test_multiple_transitions(self):
        repo = InMemoryKnowledgeRepository()
        vid = uuid.uuid4()
        t1 = make_transition(from_version_id=vid)
        t2 = make_transition(to_version_id=vid)
        repo.create_transition(t1)
        repo.create_transition(t2)

        result = repo.get_transitions_for_version(vid)
        assert len(result) == 2

    def test_get_all_transitions(self):
        repo = InMemoryKnowledgeRepository()
        t1 = make_transition()
        t2 = make_transition()
        repo.create_transition(t1)
        repo.create_transition(t2)

        result = repo.get_all_transitions()
        assert len(result) == 2


class TestInMemoryConflictStorage:
    def test_create_and_retrieve_conflict(self):
        repo = InMemoryKnowledgeRepository()
        c = make_conflict()
        repo.create_conflict(c)

        result = repo.get_conflicts()
        assert len(result) == 1
        assert result[0].id == c.id

    def test_get_conflicts_empty(self):
        repo = InMemoryKnowledgeRepository()
        result = repo.get_conflicts()
        assert result == ()

    def test_multiple_conflicts(self):
        repo = InMemoryKnowledgeRepository()
        c1 = make_conflict()
        c2 = make_conflict()
        repo.create_conflict(c1)
        repo.create_conflict(c2)

        result = repo.get_conflicts()
        assert len(result) == 2

    def test_conflict_preserves_fields(self):
        repo = InMemoryKnowledgeRepository()
        vid1 = uuid.uuid4()
        vid2 = uuid.uuid4()
        c = make_conflict(version_ids=(vid1, vid2), description="Test desc")
        repo.create_conflict(c)

        result = repo.get_conflicts()[0]
        assert result.version_ids == (vid1, vid2)
        assert result.description == "Test desc"
        assert result.status == ConflictStatus.OPEN
