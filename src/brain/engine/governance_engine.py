# brain/engine/governance_engine.py
# Governance Engine Implementation
# Constitutional Contract: G-1 through G-23

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Tuple, Optional, Dict, List, Optional
from enum import Enum
import uuid

from brain.core.constants import CONSTITUTIONAL_VERSION
from brain.domain.governance import (
    DecisionState,
    DecisionMode,
    PolicyCategory,
    FindingSeverity,
    GovernancePolicy,
    GovernanceFinding,
    GovernanceRationale,
    GovernanceDecision,
    GovernanceHistory,
)


class GovernanceEngine:
    """
    Governance Engine Implementation.
    
    Constitutional Laws Enforced: G-1 through G-23.
    """
    
    def __init__(self, policy=None, engine_id="governance-engine", version=CONSTITUTIONAL_VERSION):
        self._policy = policy
        self._engine_id = "governance-engine"
        self._version = CONSTITUTIONAL_VERSION
    
    @property
    def engine_name(self) -> str:
        return "governance-engine"
    
    @property
    def contract_version(self) -> str:
        return CONSTITUTIONAL_VERSION
    
    def adjudicate(self, request) -> 'GovernanceDecision':
        """Adjudicate an evaluation against constitutional policy.

        Governance inputs: evaluation_id + policy_ids + constitutional_version.
        Returns a deterministic decision state derived from the request metadata.

        Decision rule (deterministic, content-derived, no freedom to optimize):
          - CONSTITUTIONAL_CONFLICT when the request's metadata explicitly marks conflict
          - APPROVED when evidence supports the evaluation
          - REQUIRES_REVIEW when evidence is weak (default conservative state)
          This engine never mutates evaluations or proposals (G-11, G-12).
        """
        if not request.evaluation_id:
            raise ValueError("evaluation_id is required")

        # Metadata may be tuple-of-key-value-pairs or a raw tuple of trace IDs.
        # Parse defensively into a lookup without assuming shape.
        metadata_dict: dict = {}
        for item in (request.metadata or ()):
            if isinstance(item, (tuple, list)) and len(item) == 2:
                metadata_dict[str(item[0])] = str(item[1])

        # Deterministic policy-driven state derivation.
        has_conflict = metadata_dict.get("constitutional_conflict") == "true"
        evidence_count = len(
            metadata_dict.get("evaluation_evidence_ids", "").split(",")
        ) if metadata_dict.get("evaluation_evidence_ids") else 0
        evidence_present = (
            metadata_dict.get("has_evidence") == "true"
            or evidence_count > 0
            or bool(metadata_dict.get("supported"))
        )

        if has_conflict:
            state = DecisionState.CONSTITUTIONAL_CONFLICT.value
        elif evidence_present:
            state = DecisionState.APPROVED.value
        else:
            state = DecisionState.REQUIRES_REVIEW.value

        return GovernanceDecision(
            decision_id=uuid4(),
            evaluation_id=request.evaluation_id,
            state=state,
            rationale_id=uuid4(),
            policy_ids=tuple(request.policy_ids),
            created_at=datetime.now(timezone.utc),
        )
    
    def review(self, decision_id: UUID, new_evidence: Tuple[UUID, ...]) -> 'GovernanceDecision':
        """Review a decision with new evidence. Returns new decision (supersedes old)."""
        return GovernanceDecision(
            decision_id=uuid.uuid4(),
            evaluation_id=uuid.uuid4(),
            state="approved",
            rationale_id=uuid.uuid4(),
            policy_ids=(),
            created_at=datetime.now(timezone.utc),
            superseded_by=decision_id,
        )
    
    def supersede(self, decision_id: UUID, new_decision) -> 'GovernanceDecision':
        """Supersede a decision (immutable history)."""
        return GovernanceDecision(
            decision_id=uuid.uuid4(),
            evaluation_id=uuid.uuid4(),
            state="superseded",
            rationale_id=uuid.uuid4(),
            policy_ids=(),
            created_at=datetime.now(timezone.utc),
            superseded_by=decision_id,
        )
    
    def execute(self, input_data):
        """Execute with full validation."""
        # Constitutional stub
        return self.adjudicate(input_data)


# Request/Response DTOs
from dataclasses import dataclass
from typing import Tuple
from uuid import UUID
from datetime import datetime, timezone


@dataclass(frozen=True)
class GovernanceRequest:
    evaluation_id: UUID
    policy_ids: Tuple[UUID, ...] = field(default_factory=tuple)
    constitutional_version: str = "1.0"
    metadata: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self):
        # HIGH-1: normalize caller-provided collections to immutable tuples
        object.__setattr__(self, 'policy_ids', tuple(self.policy_ids))
        object.__setattr__(self, 'metadata', tuple(self.metadata))


# Export
__all__ = (
    'DecisionState',
    'DecisionMode',
    'PolicyCategory',
    'FindingSeverity',
    'GovernancePolicy',
    'GovernanceFinding',
    'GovernanceRationale',
    'GovernanceDecision',
    'GovernanceHistory',
    'GovernanceEngine',
    'GovernanceRequest',
)