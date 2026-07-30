from enum import Enum


class AuthorizationState(Enum):
    """
    Constitutional authorization states.

    Execution states do NOT belong here.
    """

    AUTHORIZED = "authorized"
    DENIED = "denied"
    REQUIRES_REVIEW = "requires_review"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    SUPERSEDED = "superseded"


class ConstraintType(Enum):
    """Types of constitutional constraints on authorization."""

    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    CONSTITUTIONAL_REVIEW_REQUIRED = "constitutional_review_required"
    EVIDENCE_EXPIRED = "evidence_expired"
    AUTHORIZATION_EXPIRED = "authorization_expired"
    CONFLICTING_POLICIES = "conflicting_policies"