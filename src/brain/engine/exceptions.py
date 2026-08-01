# Engine Exceptions

"""
All engine-specific exceptions for the Hermes cognitive pipeline.
"""

from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime


class EngineException(Exception):
    """Base exception for all engine errors."""
    
    def __init__(self, message: str, error_code: str = "", context: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()


class EngineConfigurationError(EngineException):
    """Raised when engine configuration is invalid."""
    pass


class EngineInputValidationError(EngineException):
    """Raised when engine input validation fails."""
    pass


class EngineOutputValidationError(EngineException):
    """Raised when engine output validation fails."""
    pass


class EngineContractViolationError(EngineException):
    """Raised when engine violates its constitutional contract."""
    pass


# Observation Engine Exceptions
class ObservationValidationError(EngineInputValidationError):
    """Raised when observation input validation fails."""
    pass


class InsufficientEvidenceError(EngineException):
    """Raised when observation evidence is insufficient."""
    pass


class InvalidSignalError(EngineInputValidationError):
    """Raised when signal data is invalid."""
    pass


# Hypothesis Engine Exceptions
class HypothesisValidationError(EngineInputValidationError):
    """Raised when hypothesis input validation fails."""
    pass


class InsufficientObservationsError(EngineInputValidationError):
    """Raised when insufficient observations for hypothesis generation."""
    pass


class PolicyViolationError(EngineException):
    """Raised when request violates policy."""
    pass


class HypothesisGenerationError(EngineException):
    """Raised when hypothesis generation fails."""
    pass


# Problem Engine Exceptions
class InsufficientHypothesesError(EngineInputValidationError):
    """Raised when insufficient hypotheses for problem formulation."""
    pass


class ProblemFormulationError(EngineException):
    """Raised when problem formulation fails."""
    pass


# Proposal Engine Exceptions
class InsufficientProblemError(EngineInputValidationError):
    """Raised when problem is insufficient for proposal generation."""
    pass


class ProposalGenerationError(EngineException):
    """Raised when proposal generation fails."""
    pass


class PolicyViolationError(EngineException):
    """Raised when request violates policy."""
    pass


# Evaluation Engine Exceptions
class InsufficientEvidenceError(EngineInputValidationError):
    """Raised when insufficient evidence for evaluation."""
    pass


class EvaluationPolicyViolationError(EngineException):
    """Raised when evaluation violates policy."""
    pass


class EvaluationError(EngineException):
    """Raised when evaluation fails."""
    pass


# Governance Engine Exceptions
class InsufficientEvidenceError(EngineInputValidationError):
    """Raised when evaluation evidence is insufficient for decision."""
    pass


class PolicyConflictError(EngineException):
    """Raised when constitutional policies conflict."""
    pass


class InsufficientPolicyError(EngineException):
    """Raised when no applicable policies for decision."""
    pass


class InvalidDecisionError(EngineException):
    """Raised when governance decision is invalid."""
    pass


# Authorization Engine Exceptions
class InvalidDecisionError(EngineException):
    """Raised when governance decision is invalid or superseded."""
    pass


class InsufficientPolicyError(EngineException):
    """Raised when no applicable policies for authorization."""
    pass


class ConstitutionalViolationError(EngineException):
    """Raised when decision violates constitutional policy."""
    pass


class AuthorizationRevokedError(EngineException):
    """Raised when authorization is revoked."""
    pass


# Execution Engine Exceptions
class AuthorizationTokenInvalidError(EngineException):
    """Raised when authorization token is invalid, revoked, or expired."""
    pass


class ExecutionPlanInvalidError(EngineException):
    """Raised when execution plan is invalid or superseded."""
    pass


class AuthorizationRevokedError(EngineException):
    """Raised when authorization has been revoked."""
    pass


class ConstitutionalViolationError(EngineException):
    """Raised when plan violates constitutional constraints."""
    pass


class ExecutionFailedError(EngineException):
    """Raised when execution fails."""
    def __init__(self, message: str, failure_type: str, error_details: str = ""):
        super().__init__(message, error_code="EXECUTION_FAILED", context={"failure_type": failure_type, "error_details": error_details})
        self.failure_type = failure_type


class AuthorizationTokenInvalidError(EngineException):
    pass


class ExecutionPlanInvalidError(EngineException):
    pass


class AuthorizationRevokedError(EngineException):
    pass


class ConstitutionalViolationError(EngineException):
    pass


# Shared base exceptions
class ValidationError(EngineException):
    """Raised when input validation fails."""
    pass


class InsufficientEvidenceError(EngineException):
    pass


class PolicyViolationError(EngineException):
    pass


class InsufficientPolicyError(EngineException):
    pass


class InvalidDecisionError(EngineException):
    pass


class PolicyConflictError(EngineException):
    pass


class InsufficientPolicyError(EngineException):
    pass


class ConstitutionalViolationError(EngineException):
    pass


class AuthorizationRevokedError(EngineException):
    pass


class InvalidDecisionError(EngineException):
    pass


class ExecutionPlanInvalidError(EngineException):
    pass


class AuthorizationTokenInvalidError(EngineException):
    pass


class AuthorizationRevokedError(EngineException):
    pass


class ConstitutionalViolationError(EngineException):
    pass


class ExecutionFailedError(EngineException):
    pass


class InsufficientEvidenceError(EngineException):
    pass


class PolicyViolationError(EngineException):
    pass


class InsufficientPolicyError(EngineException):
    pass


class AuthorizationTokenInvalidError(EngineException):
    pass


class ExecutionPlanInvalidError(EngineException):
    pass


class AuthorizationRevokedError(EngineException):
    pass


class ConstitutionalViolationError(EngineException):
    pass