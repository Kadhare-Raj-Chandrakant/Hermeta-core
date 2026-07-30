from datetime import datetime, timezone

from brain.domain.ports.knowledge_ingestion import KnowledgeIngestionPort
from brain.detection.observation import Observation
from brain.detection.pipeline import DetectionPipeline
from brain.events.publisher import EventPublisher
from brain.events.types import KnowledgeLearned
from brain.execution.report import ExecutionReport
from brain.learning.execution_feedback import ExecutionFeedback
from brain.learning.reflection_bridge import ReflectionBridge
from brain.learning.report import LearningReport
from brain.reflection.engine import ReflectionEngine
from brain.validation.engine import ValidationEngine


class LearningCoordinator:
    def __init__(
        self,
        detection: DetectionPipeline,
        validation: ValidationEngine,
        brain: KnowledgeIngestionPort,
        publisher: EventPublisher,
        reflection_engine: ReflectionEngine,
        reflection_bridge: ReflectionBridge,
        execution_feedback: ExecutionFeedback,
    ) -> None:
        self._detection = detection
        self._validation = validation
        self._brain = brain
        self._publisher = publisher
        self._reflection_engine = reflection_engine
        self._reflection_bridge = reflection_bridge
        self._execution_feedback = execution_feedback

    def learn_from_observations(
        self, observations: tuple[Observation, ...]
    ) -> LearningReport:
        start = datetime.now(timezone.utc)

        report = self._detection.run(observations)
        candidates_detected = report.candidates_produced

        accepted = 0
        rejected = 0
        for candidate in report.candidates:
            validation = self._validation.validate(candidate)
            if validation.passed:
                try:
                    self._brain.learn(candidate)
                    accepted += 1
                    self._publisher.publish(
                        KnowledgeLearned(
                            knowledge_type=candidate.knowledge_type.value,
                            title=candidate.title,
                        )
                    )
                except Exception:
                    rejected += 1
            else:
                rejected += 1

        end = datetime.now(timezone.utc)

        return LearningReport(
            observations_processed=len(observations),
            candidates_detected=candidates_detected,
            accepted=accepted,
            rejected=rejected,
            events_processed=accepted,
            reflection_findings=0,
            transitions_created=0,
            duration=end - start,
        )

    def learn_from_execution(self, report: ExecutionReport) -> LearningReport:
        observations = self._execution_feedback.to_observations(report)
        return self.learn_from_observations(observations)

    def reflect_on_knowledge(
        self, versions: tuple
    ) -> tuple:
        reflection_report = self._reflection_engine.reflect(versions)
        proposals = self._reflection_bridge.propose(reflection_report)
        applied = self._reflection_bridge.apply(proposals)
        return proposals, applied