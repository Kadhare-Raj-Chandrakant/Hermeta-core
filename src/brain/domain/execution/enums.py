from enum import Enum


class ExecutionStatus(Enum):
    """
    Execution status states.

    These represent the observable outcome of execution.
    """

    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"


class ArtifactType(Enum):
    """Types of artifacts produced by execution."""

    KNOWLEDGE_VERSION = "knowledge_version"
    EXECUTION_RECEIPT = "execution_receipt"
    LOG = "log"
    METRIC = "metric"


class FailureType(Enum):
    """Types of execution failures."""

    INVALID_INPUT = "invalid_input"
    CONSTRAINT_VIOLATION = "constraint_violation"
    EXECUTION_ERROR = "execution_error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"