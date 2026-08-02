from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import uuid

from brain.domain.enums import LifecycleState
from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_operation import EvolutionOperation
from brain.evolution.evolution_plan import EvolutionPlan
from brain.evolution.evolution_record import EvolutionRecord, OptimisticConcurrencyError
from brain.evolution.transition import KnowledgeTransition
from brain.repositories.base import KnowledgeRepository
from brain.repositories.evolution_base import EvolutionRepository


class EvolutionExecutor:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        evolution_repository: EvolutionRepository,
    ) -> None:
        self._knowledge = knowledge_repository
        self._evolution = evolution_repository

    def execute(
        self,
        plan: EvolutionPlan,
        context: EvolutionContext | None = None,
    ) -> EvolutionRecord:
        policy = context.planning_policy if context else "default"

        all_ops = plan.operations

        for i, op in enumerate(all_ops):
            current = self._knowledge.get_latest_version(op.target_id)
            if current.version_id != op.expected_version_id:
                raise OptimisticConcurrencyError(
                    operation_index=i,
                    target_id=op.target_id,
                    expected_version_id=op.expected_version_id,
                    actual_version_id=current.version_id,
                )

        for i, op in enumerate(all_ops):
            self._apply_operation(op)

        record = EvolutionRecord(
            plan_identity=_plan_identity(plan, policy),
            executed_at=datetime.now(timezone.utc),
            success=True,
            operations_count=len(all_ops),
            affected_targets=tuple(sorted(set(op.target_id for op in all_ops))),
            reason="execution_success",
            policy=policy,
        )
        self._evolution.save_execution_record(record)
        return record

    def _apply_operation(self, op: EvolutionOperation) -> None:
        current = self._knowledge.get_latest_version(op.target_id)

        tt = op.transition_type
        if tt.value == "update":
            new_state = LifecycleState.ARCHIVED
        elif tt.value == "supersedes":
            new_state = LifecycleState.ARCHIVED
        elif tt.value == "refinement":
            new_state = LifecycleState.DRAFT
        else:
            new_state = LifecycleState.ARCHIVED

        updated = replace(current, lifecycle_state=new_state)
        self._knowledge.replace_version(updated)

        transition = KnowledgeTransition(
            from_version_id=current.version_id,
            to_version_id=updated.version_id,
            transition_type=tt,
            reason=op.reason,
            confidence=1.0,
            source="evolution_executor",
        )
        self._evolution.create_transition(transition)


def _plan_identity(plan: EvolutionPlan, policy: str) -> uuid.UUID:
    """Deterministic, content-derived plan identity (E-12 / X-7).

    Replaces the earlier salted-hash implementation. Full operation formatting
    is hashed (target_id | transition_type | expected_version_id | reason) so
    that two semantically different plans cannot collide.
    """
    h = hashlib.sha256()
    op_keys = sorted(
        f"{op.target_id}|{op.transition_type.value}|{op.expected_version_id}|{op.reason}".encode("utf-8")
        for op in plan.operations
    )
    target_keys = sorted(str(t).encode("utf-8") for t in plan.affected_targets)
    h.update(b"||".join(op_keys))
    h.update(b":::")
    h.update(b"||".join(target_keys))
    h.update(b":::")
    h.update(policy.encode("utf-8"))
    return uuid.UUID(bytes=h.digest()[:16])
