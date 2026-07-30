from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class ProposalOutcome:
    """
    Represents the INTENDED cognitive outcome of a proposal.

    This is NOT a guarantee.
    This is NOT a measurable target.
    This is a QUALITATIVE description of desired cognitive effect.

    Examples:
    - "Improve retrieval quality for ambiguous queries"
    - "Reduce planning ambiguity in multi-step tasks"
    - "Increase learning consistency across similar tasks"
    - "Improve reflection finding precision"
    - "Reduce evolution approval latency"

    Forbidden:
    - Quantitative metrics (e.g., "increase accuracy by 15%")
    - Implementation mechanisms (e.g., "add LRU cache")
    - Code-level changes (e.g., "modify RetrievalEngine.score_documents")
    """

    outcome_id: uuid.UUID = uuid.uuid4()
    description: str = ""
    category: str = ""
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("description must not be empty")
        if not self.category.strip():
            raise ValueError("category must not be empty")