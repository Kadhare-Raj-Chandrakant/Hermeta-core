from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class Tradeoff:
    """
    A first-class cognitive object representing a tradeoff between benefit and cost.

    Tradeoffs are explicit cognitive objects — not flattened into free-form text.
    They represent: "We gain X, but we lose Y" or "We accept Y to gain X".

    A tradeoff has:
    - What is gained (benefit)
    - What is lost or accepted (cost)
    - The dimension/context of the tradeoff

    Tradeoffs are first-class objects because they represent reasoning,
    not just text. Future evaluations may analyze tradeoff structures.
    """

    tradeoff_id: uuid.UUID = uuid.uuid4()
    benefit: str = ""
    cost: str = ""
    dimension: str = ""
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.benefit.strip():
            raise ValueError("benefit must not be empty")
        if not self.cost.strip():
            raise ValueError("cost must not be empty")
        if not self.dimension.strip():
            raise ValueError("dimension must not be empty")