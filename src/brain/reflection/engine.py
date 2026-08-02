from datetime import datetime, timezone

from brain.domain.version import KnowledgeVersion
from brain.reflection.detector import ReflectionDetector
from brain.reflection.finding import ReflectionFinding
from brain.reflection.report import ReflectionReport


class ReflectionEngine:
    """Constitutional contract: stateless orchestrator.

    Per B.8 architecture freeze (Rule 4 in test_state_ownership), this engine
    must not hold mutable instance state. Every invocation of `reflect()` is
    reentrant and thread-safe by construction because all accumulators are
    locals bound to the method's stack frame.
    """

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
