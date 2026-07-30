from dataclasses import dataclass
from enum import Enum
import uuid


class IntentType(Enum):
    SUPERSEDE = "supersede"
    REFINE = "refine"
    ARCHIVE = "archive"
    MERGE = "merge"
    SPLIT = "split"
    RECLASSIFY = "reclassify"
    UPDATE_EVIDENCE = "update_evidence"
    ADJUST_CONFIDENCE = "adjust_confidence"


@dataclass(frozen=True)
class EvolutionIntent:
    intent_type: IntentType
    target_identity: uuid.UUID
    target_version_id: uuid.UUID
    proposed_version_id: uuid.UUID
    rationale: str
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty")