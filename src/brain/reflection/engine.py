from datetime import datetime, timezone

from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport


class ReflectionEngine:
    def __init__(self, detectors: tuple[ReflectionDetector, ...]) -> None:
        self._detectors = detectors

    def reflect(
        self, versions: tuple[KnowledgeVersion, ...]
    ) -> ReflectionReport:
        start = datetime.now(timezone.utc)
        all_findings: list[ReflectionFinding] = []
        detector_names: list[str] = []
        for detector in self._detectors:
            detector_names.append(type(detector).__name__)
            findings = detector.analyze(versions)
            all_findings.extend(findings)
        end = datetime.now(timezone.utc)
        return ReflectionReport(
            versions_checked=len(versions),
            detectors_used=tuple(detector_names),
            findings=tuple(all_findings),
            duration=end - start,
        )
