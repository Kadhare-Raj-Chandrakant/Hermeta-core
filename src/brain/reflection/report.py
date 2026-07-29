from dataclasses import dataclass
from datetime import timedelta

from brain.reflection.finding import ReflectionFinding


@dataclass(frozen=True)
class ReflectionReport:
    versions_checked: int
    detectors_used: tuple[str, ...]
    findings: tuple[ReflectionFinding, ...]
    duration: timedelta

    def __post_init__(self) -> None:
        if self.versions_checked < 0:
            raise ValueError(f"versions_checked must be >= 0, got {self.versions_checked}")
