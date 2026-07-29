import uuid
from datetime import datetime, timezone

import pytest
from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.version import KnowledgeVersion
from brain.evolution.evolution import EvolutionEngine
from brain.evolution.transition_type import TransitionType
from brain.repositories.memory import InMemoryKnowledgeRepository


def make_version(
    identity_id: uuid.UUID | None = None,
    version_number: int = 1,
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test Knowledge",
    understanding: str = "Test understanding",
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=identity_id or uuid.uuid4(),
        version_number=version_number,
        knowledge_type=knowledge_type,
        title=title,
        understanding=understanding,
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


def make_engine() -> tuple[EvolutionEngine, InMemoryKnowledgeRepository]:
    repo = InMemoryKnowledgeRepository()
    engine = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
    return engine, repo


class TestEvolveSameIdentity:
    def test_creates_update_transition(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        transition = engine.evolve(v2, previous_version=v1)

        assert transition.transition_type == TransitionType.UPDATE
        assert transition.from_version_id == v1.version_id
        assert transition.to_version_id == v2.version_id

    def test_auto_detects_previous_version(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        transition = engine.evolve(v2)

        assert transition.transition_type == TransitionType.UPDATE


class TestEvolveDifferentIdentity:
    def test_creates_supersedes_transition(self):
        engine, repo = make_engine()
        identity1 = repo.create_identity()
        identity2 = repo.create_identity()
        v1 = make_version(identity_id=identity1.id, version_number=1)
        v2 = make_version(identity_id=identity2.id, version_number=1)
        repo.add_version(v1)
        repo.add_version(v2)

        transition = engine.evolve(v2, previous_version=v1)

        assert transition.transition_type == TransitionType.SUPERSEDES


class TestEvolveExplicitTypes:
    def test_explicit_refinement(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        transition = engine.evolve(
            v2, previous_version=v1,
            transition_type=TransitionType.REFINEMENT,
            reason="More specific",
        )

        assert transition.transition_type == TransitionType.REFINEMENT

    def test_explicit_extends(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        transition = engine.evolve(
            v2, previous_version=v1,
            transition_type=TransitionType.EXTENDS,
            reason="Added capability",
        )

        assert transition.transition_type == TransitionType.EXTENDS


class TestEvolveNoPreviousVersion:
    def test_raises_when_no_previous(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)

        with pytest.raises(ValueError, match="no previous version"):
            engine.evolve(v1)


class TestEvolveDeterministic:
    def test_same_input_same_output(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        t1 = engine.evolve(v2, previous_version=v1, reason="test", confidence=0.9, source="unit")
        t2 = engine.evolve(v2, previous_version=v1, reason="test", confidence=0.9, source="unit")

        assert t1.transition_type == t2.transition_type
        assert t1.reason == t2.reason
        assert t1.confidence == t2.confidence

    def test_different_reasons_different_output(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        t1 = engine.evolve(v2, previous_version=v1, reason="reason A")
        t2 = engine.evolve(v2, previous_version=v1, reason="reason B")

        assert t1.reason != t2.reason


class TestEvolveStoredInRepository:
    def test_transition_persisted(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        engine.evolve(v2, previous_version=v1)

        transitions = repo.get_transitions_for_version(v1.version_id)
        assert len(transitions) == 1


class TestRecordConflict:
    def test_creates_conflict(self):
        engine, repo = make_engine()
        v1 = make_version()
        v2 = make_version()

        conflict = engine.record_conflict(
            version_ids=(v1.identity_id, v2.identity_id),
            description="Incompatible approaches",
        )

        assert len(conflict.version_ids) == 2
        assert conflict.description == "Incompatible approaches"

    def test_creates_contradicts_transition(self):
        engine, repo = make_engine()
        v1 = make_version()
        v2 = make_version()

        engine.record_conflict(
            version_ids=(v1.identity_id, v2.identity_id),
            description="Contradiction detected",
        )

        transitions = repo.get_transitions_for_version(v1.identity_id)
        contradict_transitions = [t for t in transitions if t.transition_type == TransitionType.CONTRADICTS]
        assert len(contradict_transitions) == 1

    def test_conflict_persisted(self):
        engine, repo = make_engine()
        v1 = make_version()
        v2 = make_version()

        engine.record_conflict(
            version_ids=(v1.identity_id, v2.identity_id),
            description="Test",
        )

        conflicts = repo.get_conflicts()
        assert len(conflicts) == 1


class TestGetTransitions:
    def test_returns_empty_for_unknown(self):
        engine, _ = make_engine()
        result = engine.get_transitions(uuid.uuid4())
        assert result == ()

    def test_returns_transitions_for_version(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        engine.evolve(v2, previous_version=v1)
        engine.evolve(v2, previous_version=v1, reason="second")

        result = engine.get_transitions(v1.version_id)
        assert len(result) == 2


class TestGetAllTransitions:
    def test_returns_empty_initially(self):
        engine, _ = make_engine()
        assert engine.get_all_transitions() == ()

    def test_returns_all(self):
        engine, repo = make_engine()
        identity = repo.create_identity()
        v1 = make_version(identity_id=identity.id, version_number=1)
        v2 = make_version(identity_id=identity.id, version_number=2)
        repo.add_version(v1)
        repo.add_version(v2)

        engine.evolve(v2, previous_version=v1)
        assert len(engine.get_all_transitions()) == 1


class TestGetConflicts:
    def test_returns_empty_initially(self):
        engine, _ = make_engine()
        assert engine.get_conflicts() == ()
