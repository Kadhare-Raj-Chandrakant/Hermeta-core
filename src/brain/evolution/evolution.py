from brain.domain.version import KnowledgeVersion
from brain.evolution.conflict import Conflict
from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_operation import EvolutionOperation
from brain.evolution.evolution_plan import EvolutionPlan
from brain.evolution.planning import EvolutionPlanner
from brain.evolution.transition import KnowledgeTransition
from brain.evolution.transition_type import TransitionType
from brain.repositories.base import KnowledgeRepository
from brain.repositories.evolution_base import EvolutionRepository


class EvolutionEngine:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository | None = None,
        evolution_repository: EvolutionRepository | None = None,
        planner: EvolutionPlanner | None = None,
    ) -> None:
        self._knowledge = knowledge_repository
        self._evolution = evolution_repository
        self._planner = planner or EvolutionPlanner()

    def _plan(
        self,
        targets: tuple,
        category: str,
        context: EvolutionContext,
    ) -> EvolutionPlan:
        return self._planner.plan(targets, category, context)

    def evolve(
        self,
        new_version: KnowledgeVersion,
        previous_version: KnowledgeVersion | None = None,
        transition_type: TransitionType | None = None,
        reason: str = "",
        confidence: float = 1.0,
        source: str = "system",
    ) -> KnowledgeTransition:
        if previous_version is None:
            all_versions = self._knowledge.list_versions(new_version.identity_id)
            prior = [v for v in all_versions if v.version_number < new_version.version_number]
            if prior:
                previous_version = max(prior, key=lambda v: v.version_number)

        if previous_version is None:
            raise ValueError("Cannot create transition: no previous version found")

        if transition_type is None:
            if previous_version.identity_id == new_version.identity_id:
                transition_type = TransitionType.UPDATE
            else:
                transition_type = TransitionType.SUPERSEDES

        if not reason:
            reason = f"Version {previous_version.version_number} to {new_version.version_number}"

        transition = KnowledgeTransition(
            from_version_id=previous_version.version_id,
            to_version_id=new_version.version_id,
            transition_type=transition_type,
            reason=reason,
            confidence=confidence,
            source=source,
        )

        self._evolution.create_transition(transition)
        return transition

    def record_conflict(
        self,
        version_ids: tuple,
        description: str,
        resolution: str | None = None,
    ) -> Conflict:
        conflict = Conflict(
            version_ids=version_ids,
            description=description,
            resolution=resolution,
        )

        self._evolution.create_conflict(conflict)

        transition = KnowledgeTransition(
            from_version_id=version_ids[0],
            to_version_id=version_ids[1],
            transition_type=TransitionType.CONTRADICTS,
            reason=description,
            confidence=1.0,
            source="conflict_detection",
        )
        self._evolution.create_transition(transition)

        return conflict

    def get_transitions(self, version_id) -> tuple:
        return self._evolution.get_transitions_for_version(version_id)

    def get_all_transitions(self) -> tuple:
        return self._evolution.get_all_transitions()

    def get_conflicts(self) -> tuple:
        return self._evolution.get_conflicts()
