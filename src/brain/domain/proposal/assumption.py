from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ProposalAssumption:
    """
    An assumption under which a proposal may be useful.

    Assumptions are DESCRIPTIVE only.
    They are NOT evaluative.
    They do NOT express confidence.
    They do NOT predict outcomes.

    Examples:
    - "Workload consists primarily of point lookups"
    - "Architecture allows pluggable retrieval backends"
    - "Environment provides consistent latency < 10ms"
    """

    assumption_id: uuid.UUID = uuid.uuid4()
    description: str = ""
    category: str = ""
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not self.category.strip():
            raise ValueError("category must not be empty")