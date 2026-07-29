from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

from brain.evolution.evolution import EvolutionEngine
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport
from brain.reflection.type import ReflectionType
from brain.repositories.evolution_base import EvolutionRepository


@dataclass(frozen=True)
class EvolutionProposal:
    finding_id: uuid.UUID
    reflection_type: str
    affected_versions: tuple[uuid.UUID, ...]
    explanation: str
    confidence: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ReflectionBridge:
    def __init__(
        self,
        evolution_engine: EvolutionEngine,
        evolution_repository: EvolutionRepository,
    ) -> None:
        self._evolution = evolution_engine
        self._repo = evolution_repository

    def propose(self, report: ReflectionReport) -> tuple[EvolutionProposal, ...]:
        proposals: list[EvolutionProposal] = []
        for finding in report.findings:
            proposal = EvolutionProposal(
                finding_id=finding.id,
                reflection_type=finding.reflection_type.value,
                affected_versions=finding.affected_versions,
                explanation=finding.explanation,
                confidence=finding.confidence,
            )
            proposals.append(proposal)
        return tuple(proposals)

    def apply(self, proposals: tuple[EvolutionProposal, ...]) -> int:
        applied = 0
        for proposal in proposals:
            if len(proposal.affected_versions) >= 2:
                from_id = proposal.affected_versions[0]
                to_id = proposal.affected_versions[1]

                if proposal.reflection_type == ReflectionType.CONFLICT.value:
                    self._evolution.record_conflict(
                        version_ids=proposal.affected_versions,
                        description=proposal.explanation,
                        resolution=None,
                    )
                    applied += 1
                elif proposal.reflection_type in (
                    ReflectionType.DUPLICATE.value,
                    ReflectionType.OBSOLETE.value,
                ):
                    transition = KnowledgeTransition(
                        from_version_id=from_id,
                        to_version_id=to_id,
                        transition_type=TransitionType.SUPERSEDES,
                        reason=proposal.explanation,
                        confidence=proposal.confidence,
                        source="reflection",
                    )
                    self._repo.create_transition(transition)
                    applied += 1
        return applied
