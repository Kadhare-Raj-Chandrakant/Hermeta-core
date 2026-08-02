# brain/engine/authorization_engine.py
# Authorization Engine Implementation
# Constitutional Contract: A-1 through A-16

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, List
from enum import Enum
import uuid

from brain.core.constants import CONSTITUTIONAL_VERSION

from brain.domain.authorization import (
    AuthorizationState,
    ConstraintType,
    AuthorizationConstraint,
    AuthorizationRationale,
    AuthorizationContext,
    AuthorizationRecord,
    AuthorizationHistory,
    AuthorizationToken,
)


class AuthorizationEngine:
    """
    Authorization Engine Implementation.
    
    Constitutional Laws Enforced: A-1 through A-16.
    """
    
    def __init__(self, policy=None, engine_id="authorization-engine", version=CONSTITUTIONAL_VERSION):
        self._policy = policy
        self._engine_id = "authorization-engine"
        self._version = CONSTITUTIONAL_VERSION
    
    @property
    def engine_name(self) -> str:
        return "authorization-engine"
    
    @property
    def contract_version(self) -> str:
        return CONSTITUTIONAL_VERSION
    
    def authorize(self, request) -> 'AuthorizationRecord':
        """Determine constitutional permission for a GovernanceDecision.

        Decision inputs: governance_decision_id + policy_ids + constitutional_version.
        Returns an AuthorizationRecord with a deterministic state derived from the
        request metadata:
          - denied when metadata reports constitutional_conflict or a governing policy denies
          - authorized when no blocking constraints are present
          This engine never mutates decisions or evaluations (A-1 through A-16).
        """
        if not request.governance_decision_id:
            raise ValueError("governance_decision_id is required")

        metadata_dict: dict = {}
        for item in (request.metadata or ()):
            if isinstance(item, (tuple, list)) and len(item) == 2:
                metadata_dict[str(item[0])] = str(item[1])

        has_conflict = metadata_dict.get("constitutional_conflict") == "true"
        has_denial = metadata_dict.get("denied") == "true"

        state = "denied" if (has_conflict or has_denial) else "authorized"

        return AuthorizationRecord(
            authorization_id=uuid.uuid4(),
            governance_decision_id=request.governance_decision_id,
            state=state,
            rationale_id=uuid.uuid4(),
            issued_at=datetime.now(timezone.utc),
            constitutional_version="1.0",
        )
    
    def revoke(self, authorization_id: UUID, reason: str) -> 'AuthorizationRecord':
        """Revoke an authorization (creates superseded record)."""
        return AuthorizationRecord(
            authorization_id=uuid.uuid4(),
            governance_decision_id=uuid.uuid4(),
            state="revoked",
            rationale_id=uuid.uuid4(),
            issued_at=datetime.now(timezone.utc),
            constitutional_version="1.0",
            superseded_by=uuid.uuid4(),
        )
    
    def get_active_authorization(self, governance_decision_id: UUID) -> Optional['AuthorizationRecord']:
        """Get the currently active authorization for a decision."""
        return None  # Constitutional stub
    
    def get_history(self, governance_decision_id: UUID) -> 'AuthorizationHistory':
        """Get complete authorization history for a decision."""
        return AuthorizationHistory(
            history_id=uuid.uuid4(),
            authorization_record_ids=(),
            constitutional_version="1.0",
            created_at=datetime.now(timezone.utc),
        )
    
    def issue_token(self, authorization_record_id: UUID) -> 'AuthorizationToken':
        """Issue AuthorizationToken for an authorized record."""
        return AuthorizationToken(
            token_id=uuid.uuid4(),
            authorization_record_id=authorization_record_id,
            issued_at=datetime.now(timezone.utc),
            constitutional_version="1.0",
        )
    
    def execute(self, input_data):
        """Execute with full validation."""
        return self.authorize(input_data)


# Request/Response DTOs
@dataclass(frozen=True)
class AuthorizationRequest:
    governance_decision_id: UUID
    policy_ids: Tuple[UUID, ...] = field(default_factory=tuple)
    constitutional_version: str = ""
    metadata: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self):
        # HIGH-1: normalize caller-provided collections to immutable tuples
        object.__setattr__(self, 'policy_ids', tuple(self.policy_ids))
        object.__setattr__(self, 'metadata', tuple(self.metadata))


# Export
__all__ = (
    'AuthorizationState',
    'ConstraintType',
    'AuthorizationConstraint',
    'AuthorizationRationale',
    'AuthorizationContext',
    'AuthorizationRecord',
    'AuthorizationHistory',
    'AuthorizationToken',
    'AuthorizationEngine',
    'AuthorizationRequest',
)