from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class LearningReport:
    observations_processed: int
    candidates_detected: int
    accepted: int
    rejected: int
    events_processed: int
    reflection_findings: int
    transitions_created: int
    duration: timedelta
