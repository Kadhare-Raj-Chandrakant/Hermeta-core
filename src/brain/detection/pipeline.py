from datetime import datetime, timezone

from brain.detection.detector import KnowledgeDetector
from brain.detection.observation import Observation
from brain.detection.report import DetectionReport
from brain.pipeline.candidate import KnowledgeCandidate


class DetectionPipeline:
    def __init__(
        self,
        detectors: tuple[KnowledgeDetector, ...],
    ) -> None:
        self._detectors = detectors

    def run(self, observations: tuple[Observation, ...]) -> DetectionReport:
        start = datetime.now(timezone.utc)

        all_candidates: list[KnowledgeCandidate] = []
        for observation in observations:
            for detector in self._detectors:
                candidates = detector.detect(observation)
                all_candidates.extend(candidates)

        end = datetime.now(timezone.utc)

        return DetectionReport(
            observations_processed=len(observations),
            candidates_produced=len(all_candidates),
            candidates=tuple(all_candidates),
            detectors_used=tuple(type(d).__name__ for d in self._detectors),
            duration=end - start,
        )
