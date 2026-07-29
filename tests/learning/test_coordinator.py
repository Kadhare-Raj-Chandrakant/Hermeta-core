import uuid

import pytest

from brain.application.brain_service import BrainService
from brain.detection.detector import KnowledgeDetector
from brain.detection.observation import Observation
from brain.detection.pipeline import DetectionPipeline
from brain.domain.enums import KnowledgeType
from brain.domain.task import Task, TaskType, Priority
from brain.events.publisher import EventPublisher
from brain.events.types import KnowledgeLearned
from brain.events.subscriber import EventSubscriber
from brain.events.event import Event
from brain.evolution.evolution import EvolutionEngine
from brain.execution.context import ExecutionContext
from brain.execution.report import ExecutionReport
from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.learning.coordinator import LearningCoordinator
from brain.learning.execution_feedback import ExecutionFeedback
from brain.learning.reflection_bridge import ReflectionBridge
from brain.learning.report import LearningReport
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence
from brain.reflection.engine import ReflectionEngine
from brain.repositories.memory import InMemoryKnowledgeRepository
from brain.services.compiler import ContextCompiler
from brain.services.relevance import RelevanceEngine
from brain.services.selection import SelectionEngine
from brain.validation.engine import ValidationEngine
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.rules.type_rules import TypeRules
from brain.pipeline.version_creator import VersionCreator
from datetime import datetime, timezone, timedelta


class SimpleDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        return (
            KnowledgeCandidate(
                knowledge_type=KnowledgeType.DISCOVERY,
                title="Discovered from " + observation.source_type,
                understanding="Understanding derived from observation content: " + observation.content,
                confidence=0.8,
                evidence_source=Evidence(
                    source_type=observation.source_type,
                    content=observation.content,
                ),
            ),
        )


class EmptyDetector(KnowledgeDetector):
    def detect(self, observation: Observation) -> tuple[KnowledgeCandidate, ...]:
        return ()


def _make_task() -> Task:
    return Task(
        task_type=TaskType.IMPLEMENT,
        project="test",
        component="core",
        objective="Test objective",
        constraints=(),
        priority=Priority.MEDIUM,
    )


def _make_runtime():
    repository = InMemoryKnowledgeRepository()
    validation_engine = ValidationEngine(
        rules=(ConfidenceRule(), CompletenessRule(), EvidenceRule(), TypeRules())
    )
    version_creator = VersionCreator()
    relevance_engine = RelevanceEngine()
    selection_engine = SelectionEngine()
    context_compiler = ContextCompiler()

    brain_service = BrainService(
        repository=repository,
        validator=validation_engine,
        version_creator=version_creator,
        relevance_engine=relevance_engine,
        selection_engine=selection_engine,
        context_compiler=context_compiler,
    )

    detection = DetectionPipeline(detectors=(SimpleDetector(),))
    publisher = EventPublisher()

    reflection_engine = ReflectionEngine(detectors=())
    evolution_engine = EvolutionEngine(
        knowledge_repository=repository,
        evolution_repository=repository,
    )
    reflection_bridge = ReflectionBridge(
        evolution_engine=evolution_engine,
        evolution_repository=repository,
    )
    execution_feedback = ExecutionFeedback()

    coordinator = LearningCoordinator(
        detection=detection,
        validation=validation_engine,
        brain=brain_service,
        publisher=publisher,
        reflection_engine=reflection_engine,
        reflection_bridge=reflection_bridge,
        execution_feedback=execution_feedback,
    )

    return coordinator, repository, publisher


class TestLearningCoordinatorObservations:
    def test_learn_from_observations(self):
        coordinator, repository, publisher = _make_runtime()
        obs = (Observation(source_type="conversation", content="We chose PostgreSQL"),)

        report = coordinator.learn_from_observations(obs)

        assert isinstance(report, LearningReport)
        assert report.observations_processed == 1
        assert report.candidates_detected == 1
        assert report.accepted == 1
        assert report.rejected == 0
        assert len(repository.list_all_versions()) == 1

    def test_learn_publishes_events(self):
        coordinator, repository, publisher = _make_runtime()

        class EventCollector(EventSubscriber):
            def __init__(self) -> None:
                self.events: list[Event] = []
            def handle(self, event: Event) -> None:
                self.events.append(event)

        collector = EventCollector()
        publisher.subscribe(collector)

        obs = (Observation(source_type="conversation", content="Test knowledge"),)
        coordinator.learn_from_observations(obs)

        assert len(collector.events) == 1
        assert isinstance(collector.events[0], KnowledgeLearned)

    def test_learn_empty_observations(self):
        coordinator, repository, publisher = _make_runtime()

        report = coordinator.learn_from_observations(())

        assert report.observations_processed == 0
        assert report.candidates_detected == 0
        assert report.accepted == 0
        assert len(repository.list_all_versions()) == 0

    def test_learn_multiple_observations(self):
        coordinator, repository, publisher = _make_runtime()
        obs = (
            Observation(source_type="conversation", content="First knowledge"),
            Observation(source_type="git", content="Second knowledge"),
        )

        report = coordinator.learn_from_observations(obs)

        assert report.observations_processed == 2
        assert report.candidates_detected == 2
        assert report.accepted == 2
        assert len(repository.list_all_versions()) == 2

    def test_deterministic_behavior(self):
        coordinator, repository, publisher = _make_runtime()
        obs = (Observation(source_type="conversation", content="Deterministic test"),)

        r1 = coordinator.learn_from_observations(obs)
        r2 = coordinator.learn_from_observations(obs)

        assert r1.observations_processed == r2.observations_processed
        assert r1.candidates_detected == r2.candidates_detected
        assert r1.accepted == r2.accepted


class TestLearningCoordinatorExecution:
    def test_learn_from_execution(self):
        coordinator, repository, publisher = _make_runtime()
        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.COMPLETED,
                started_at=now,
                completed_at=now,
            ),
            success=True,
            output="Deployed successfully",
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        learning_report = coordinator.learn_from_execution(report)

        assert isinstance(learning_report, LearningReport)
        assert learning_report.observations_processed == 1
        assert learning_report.accepted == 1
        assert len(repository.list_all_versions()) == 1

    def test_learn_from_execution_failure(self):
        coordinator, repository, publisher = _make_runtime()
        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.FAILED,
                started_at=now,
                completed_at=now,
            ),
            success=False,
            output="",
            error="Connection refused",
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        learning_report = coordinator.learn_from_execution(report)

        assert learning_report.observations_processed == 1
        assert learning_report.candidates_detected == 1

    def test_learn_from_empty_execution(self):
        coordinator, repository, publisher = _make_runtime()
        now = datetime.now(timezone.utc)
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(),
            started_at=now,
            completed_at=now,
        )

        learning_report = coordinator.learn_from_execution(report)

        assert learning_report.observations_processed == 0


class TestLearningCoordinatorReflection:
    def test_reflect_on_knowledge(self):
        coordinator, repository, publisher = _make_runtime()

        proposals, applied = coordinator.reflect_on_knowledge(())

        assert isinstance(proposals, tuple)
        assert applied == 0


class TestLearningCoordinatorNoDuplicatedLearning:
    def test_each_observation_produces_one_candidate(self):
        coordinator, repository, publisher = _make_runtime()
        obs = (Observation(source_type="conversation", content="Single observation"),)

        report = coordinator.learn_from_observations(obs)

        assert report.candidates_detected == 1
        assert report.accepted == 1
        assert len(repository.list_all_versions()) == 1
