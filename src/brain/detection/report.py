from dataclasses import dataclass
from datetime import timedelta

from brain.pipeline.candidate import KnowledgeCandidate


@dataclass(frozen=True)
class DetectionReport:
    observations_processed: int
    candidates_produced: int
    candidates: tuple[KnowledgeCandidate, ...]
    detectors_used: tuple[str, ...]
    duration: timedelta
