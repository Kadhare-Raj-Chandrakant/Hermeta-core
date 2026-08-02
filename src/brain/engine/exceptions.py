# Engine Exceptions

"""
All engine-specific exceptions for the Hermes cognitive pipeline.

Each exception is defined exactly once. Names are part of the public engine
contract and must not be removed; importing engines rely on them.
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


# ---------------------------------------------------------------------------
# Pipeline-level exceptions
# ---------------------------------------------------------------------------


class PipelineExecutionError(EngineException):
    """Raised when the multi-engine pipeline fails at a specific stage.

    Carries context for diagnosis without exposing internal call sites.
    """

    def __init__(
        self,
        message: str,
        *,
        stage: str = "",
        originating_engine: str = "",
        original_exception: Optional[BaseException] = None,
        error_code: str = "PIPELINE_EXECUTION_FAILED",
        context: dict = None,
    ):
        merged_context = dict(context or {})
        merged_context.setdefault("stage", stage)
        merged_context.setdefault("originating_engine", originating_engine)
        if original_exception is not None:
            merged_context.setdefault("original_exception", repr(original_exception))
        super().__init__(message, error_code=error_code, context=merged_context)
        self.stage = stage
        self.originating_engine = originating_engine
        self.original_exception = original_exception


# ---------------------------------------------------------------------------
# Base engine exceptions
# ---------------------------------------------------------------------------


class EngineConfigurationError(EngineException):
    """Raised when engine configuration is invalid."""


class EngineInputValidationError(EngineException):
    """Raised when engine input validation fails."""


class EngineOutputValidationError(EngineException):
    """Raised when engine output validation fails."""


class EngineContractViolationError(EngineException):
    """Raised when engine violates its constitutional contract."""


# ---------------------------------------------------------------------------
# Observation Engine Exceptions
# ---------------------------------------------------------------------------
class ObservationValidationError(EngineInputValidationError):
    """Raised when observation input validation fails."""


class InvalidSignalError(EngineInputValidationError):
    """Raised when signal data is invalid."""


# ---------------------------------------------------------------------------
# Hypothesis Engine Exceptions
# ---------------------------------------------------------------------------
class HypothesisValidationError(EngineInputValidationError):
    """Raised when hypothesis input validation fails."""


class InsufficientObservationsError(EngineInputValidationError):
    """Raised when insufficient observations for hypothesis generation."""


class HypothesisGenerationError(EngineException):
    """Raised when hypothesis generation fails."""


# ---------------------------------------------------------------------------
# Problem Engine Exceptions
# ---------------------------------------------------------------------------
class InsufficientHypothesesError(EngineInputValidationError):
    """Raised when insufficient hypotheses for problem formulation."""


class ProblemFormulationError(EngineException):
    """Raised when problem formulation fails."""


# ---------------------------------------------------------------------------
# Proposal Engine Exceptions
# ---------------------------------------------------------------------------
class InsufficientProblemError(EngineInputValidationError):
    """Raised when problem is insufficient for proposal generation."""


class ProposalGenerationError(EngineException):
    """Raised when proposal generation fails."""


# ---------------------------------------------------------------------------
# Evaluation Engine Exceptions
# ---------------------------------------------------------------------------
class EvaluationPolicyViolationError(EngineException):
    """Raised when evaluation violates policy."""


class EvaluationError(EngineException):
    """Raised when evaluation fails."""


# ---------------------------------------------------------------------------
# Governance Engine Exceptions
# ---------------------------------------------------------------------------
class PolicyConflictError(EngineException):
    """Raised when constitutional policies conflict."""


class InvalidDecisionError(EngineException):
    """Raised when governance decision is invalid."""


# ---------------------------------------------------------------------------
# Authorization Engine Exceptions
# ---------------------------------------------------------------------------
class ConstitutionalViolationError(EngineException):
    """Raised when a decision or plan violates constitutional constraints."""


class AuthorizationRevokedError(EngineException):
    """Raised when an authorization has been revoked."""


# ---------------------------------------------------------------------------
# Execution Engine Exceptions
# ---------------------------------------------------------------------------
class AuthorizationTokenInvalidError(EngineException):
    """Raised when an authorization token is invalid, revoked, or expired."""


class ExecutionPlanInvalidError(EngineException):
    """Raised when an execution plan is invalid or superseded."""


class ExecutionFailedError(EngineException):
    """Raised when execution fails."""

    def __init__(self, message: str, failure_type: str = "", error_details: str = ""):
        super().__init__(
            message,
            error_code="EXECUTION_FAILED",
            context={"failure_type": failure_type, "error_details": error_details},
        )
        self.failure_type = failure_type


# ---------------------------------------------------------------------------
# Shared base exceptions
# ---------------------------------------------------------------------------
class InsufficientEvidenceError(EngineException):
    """Raised when available evidence is insufficient for the required operation."""


class PolicyViolationError(EngineException):
    """Raised when a request violates policy."""


class InsufficientPolicyError(EngineException):
    """Raised when no applicable policy exists for the operation."""


class ValidationError(EngineException):
    """Raised when input validation fails."""
