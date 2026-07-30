from enum import Enum


class DecisionState(Enum):
    """
    Constitutional decision states.

    These are the ONLY states a governance decision can take.
    Execution is NOT a decision state.
    """

    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONSTITUTIONAL_CONFLICT = "constitutional_conflict"
    REQUIRES_REVIEW = "requires_review"
    WITHDRAWN = "withdrawn"
    SUPERSEDED = "superseded"


class PolicyCategory(Enum):
    """Categories of constitutional policies."""

    ARCHITECTURAL_INTEGRITY = "architectural_integrity"
    STATE_OWNERSHIP = "state_ownership"
    DEPENDENCY_DIRECTION = "dependency_direction"
    TRANSACTION_BOUNDARIES = "transaction_boundaries"
    FAILURE_ISOLATION = "failure_isolation"
    RECOVERY_OWNERSHIP = "recovery_ownership"
    CONTRACT_COMPLIANCE = "contract_compliance"
    EVOLUTION_SAFETY = "evolution_safety"


class FindingSeverity(Enum):
    """Severity of a governance finding."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class DecisionMode(Enum):
    """How the governance decision was made."""

    CONSTITUTIONAL = "constitutional"
    HUMAN_REVIEW = "human_review"
    AUTOMATED_POLICY = "automated_policy"
    EMERGENCY = "emergency"