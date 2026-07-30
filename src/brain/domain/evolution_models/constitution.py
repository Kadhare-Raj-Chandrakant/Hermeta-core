from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from brain.domain.evolution_models.audit import AuditEventType, EvolutionAuditEntry
from brain.domain.evolution_models.approval import ApprovalStatus, EvolutionApproval
from brain.domain.evolution_models.execution import ExecutionResult, ExecutionStatus
from brain.domain.evolution_models.policy import EvolutionPolicy


@dataclass(frozen=True)
class EvolutionConstitution:
    current_policy: EvolutionPolicy
    audit_log: tuple[EvolutionAuditEntry, ...] = ()
    created_at: datetime = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc))

    def with_policy(self, new_policy: EvolutionPolicy) -> "EvolutionConstitution":
        return EvolutionConstitution(
            current_policy=new_policy,
            audit_log=self.audit_log,
            created_at=self.created_at,
        )

    def with_audit_entry(
        self,
        event_type: AuditEventType,
        actor: str,
        plan_id: uuid.UUID | None = None,
        trigger_id: uuid.UUID | None = None,
        details: tuple[tuple[str, str], ...] = (),
    ) -> "EvolutionConstitution":
        entry = EvolutionAuditEntry(
            event_id=uuid.uuid4(),
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            plan_id=plan_id,
            trigger_id=trigger_id,
            details=details,
        )
        return EvolutionConstitution(
            current_policy=self.current_policy,
            audit_log=self.audit_log + (entry,),
            created_at=self.created_at,
        )

    def is_quarantined(self, identity_id: uuid.UUID) -> bool:
        return identity_id in self.current_policy.quarantined_identities

    def intent_allowed(self, intent_type: str) -> bool:
        allowed = self.current_policy.allowed_intent_types
        if not allowed:
            return True
        return intent_type in allowed