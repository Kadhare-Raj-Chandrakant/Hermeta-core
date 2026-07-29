import uuid

import pytest

from brain.evolution.conflict import Conflict
from brain.evolution.evolution import EvolutionEngine
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.learning.reflection_bridge import EvolutionProposal, ReflectionBridge
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport
from brain.reflection.type import ReflectionType
from brain.repositories.memory import InMemoryKnowledgeRepository
from datetime import timedelta


def _make_finding(
    reflection_type: ReflectionType,
    affected_versions: tuple[uuid.UUID, ...] = (),
    explanation: str = "test finding",
    confidence: float = 0.8,
) -> ReflectionFinding:
    return ReflectionFinding(
        reflection_type=reflection_type,
        affected_versions=affected_versions,
        explanation=explanation,
        confidence=confidence,
    )


def _make_report(
    *findings: ReflectionFinding,
) -> ReflectionReport:
    return ReflectionReport(
        versions_checked=10,
        detectors_used=("DuplicateDetector",),
        findings=tuple(findings),
        duration=timedelta(seconds=0.1),
    )


class TestEvolutionProposal:
    def test_create_proposal(self):
        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="duplicate",
            affected_versions=(vid1, vid2),
            explanation="Same knowledge",
            confidence=0.9,
        )
        assert proposal.reflection_type == "duplicate"
        assert len(proposal.affected_versions) == 2
        assert isinstance(proposal.id, uuid.UUID)

    def test_proposal_is_frozen(self):
        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="duplicate",
            affected_versions=(uuid.uuid4(),),
            explanation="test",
            confidence=0.5,
        )
        with pytest.raises(AttributeError):
            proposal.explanation = "changed"


class TestReflectionBridgePropose:
    def test_propose_from_report(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        finding = _make_finding(
            ReflectionType.DUPLICATE,
            affected_versions=(vid1, vid2),
            explanation="Duplicate knowledge detected",
        )
        report = _make_report(finding)

        proposals = bridge.propose(report)

        assert len(proposals) == 1
        assert proposals[0].reflection_type == "duplicate"
        assert proposals[0].affected_versions == (vid1, vid2)

    def test_propose_empty_report(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        report = _make_report()
        proposals = bridge.propose(report)

        assert len(proposals) == 0

    def test_propose_multiple_findings(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        f1 = _make_finding(ReflectionType.DUPLICATE, explanation="dup1")
        f2 = _make_finding(ReflectionType.CONFLICT, explanation="conflict1")
        f3 = _make_finding(ReflectionType.OBSOLETE, explanation="old1")
        report = _make_report(f1, f2, f3)

        proposals = bridge.propose(report)

        assert len(proposals) == 3
        types = {p.reflection_type for p in proposals}
        assert types == {"duplicate", "conflict", "obsolete"}


class TestReflectionBridgeApply:
    def test_apply_conflict_creates_conflict(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="conflict",
            affected_versions=(vid1, vid2),
            explanation="Conflicting knowledge",
            confidence=0.9,
        )

        applied = bridge.apply((proposal,))

        assert applied == 1
        conflicts = repo.get_conflicts()
        assert len(conflicts) == 1

    def test_apply_duplicate_creates_transition(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="duplicate",
            affected_versions=(vid1, vid2),
            explanation="Duplicate detected",
            confidence=0.8,
        )

        applied = bridge.apply((proposal,))

        assert applied == 1
        transitions = repo.get_all_transitions()
        assert len(transitions) == 1
        assert transitions[0].transition_type == TransitionType.SUPERSEDES

    def test_apply_obsolete_creates_transition(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="obsolete",
            affected_versions=(vid1, vid2),
            explanation="Older version",
            confidence=0.7,
        )

        applied = bridge.apply((proposal,))

        assert applied == 1
        transitions = repo.get_all_transitions()
        assert len(transitions) == 1

    def test_apply_gap_does_not_create_transition(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        proposal = EvolutionProposal(
            finding_id=uuid.uuid4(),
            reflection_type="gap",
            affected_versions=(),
            explanation="Missing knowledge",
            confidence=1.0,
        )

        applied = bridge.apply((proposal,))

        assert applied == 0
        assert len(repo.get_all_transitions()) == 0
        assert len(repo.get_conflicts()) == 0

    def test_apply_empty_proposals(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        applied = bridge.apply(())

        assert applied == 0

    def test_propose_then_apply_integration(self):
        repo = InMemoryKnowledgeRepository()
        evolution = EvolutionEngine(knowledge_repository=repo, evolution_repository=repo)
        bridge = ReflectionBridge(evolution_engine=evolution, evolution_repository=repo)

        vid1, vid2 = uuid.uuid4(), uuid.uuid4()
        finding = _make_finding(
            ReflectionType.CONFLICT,
            affected_versions=(vid1, vid2),
            explanation="Direct conflict between two versions",
        )
        report = _make_report(finding)

        proposals = bridge.propose(report)
        applied = bridge.apply(proposals)

        assert applied == 1
        assert len(repo.get_conflicts()) == 1
