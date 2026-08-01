from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ExecutionArtifact:
    """
    An artifact produced by execution.

    Artifacts are pure data containers. They never evaluate themselves.
    """

    artifact_id: uuid.UUID
    created_at: datetime
    artifact_type: str = ""
    reference: str = ""

    def __post_init__(self) -> None:
        if not self.artifact_type.strip():
            raise ValueError("artifact_type must not be empty")
        if not self.reference.strip():
            raise ValueError("reference must not be empty")