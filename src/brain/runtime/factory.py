from brain.adapter.adapter import BrainAdapter
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.task_mapper import TaskMapper
from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.brain_service import BrainService
from brain.application.brain_session import BrainSession
from brain.application.maintenance.service import ReflectionMaintenanceService
from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.planning import PlanningUseCase
from brain.application.usecases.reflection import ReflectionUseCase
from brain.application.workflow.workflow import BrainWorkflow
from brain.detection.pipeline import DetectionPipeline
from brain.evolution.evolution import EvolutionEngine
from brain.events.publisher import EventPublisher
from brain.execution.executor import ExecutionEngine
from brain.execution.handlers.registry import HandlerRegistry
from brain.execution.policy import ExecutionPolicy
from brain.infrastructure.sqlite.repository import SQLiteKnowledgeRepository
from brain.learning.coordinator import LearningCoordinator
from brain.learning.execution_feedback import ExecutionFeedback
from brain.learning.reflection_bridge import ReflectionBridge
from brain.pipeline.version_creator import VersionCreator
from brain.planning.planner import PlanningEngine
from brain.planning.strategies.sequential import SequentialStrategy
from brain.reflection.detectors.conflict import ConflictDetector
from brain.reflection.detectors.duplicate import DuplicateDetector
from brain.reflection.detectors.gap import GapDetector
from brain.reflection.detectors.obsolete import ObsoleteDetector
from brain.reflection.engine import ReflectionEngine
from brain.repositories.memory import InMemoryKnowledgeRepository
from brain.retrieval.engine import RetrievalTriggerEngine
from brain.retrieval.trigger import RetrievalTrigger
from brain.runtime.runtime import BrainRuntime
from brain.services.compiler import ContextCompiler
from brain.services.relevance import RelevanceEngine
from brain.services.selection import SelectionEngine
from brain.validation.engine import ValidationEngine
from brain.validation.rules.completeness import CompletenessRule
from brain.validation.rules.confidence import ConfidenceRule
from brain.validation.rules.evidence import EvidenceRule
from brain.validation.rules.type_rules import TypeRules


def _create_common_components(repository):
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

    brain_session = BrainSession(brain=brain_service)

    retrieval_engine = RetrievalTriggerEngine(triggers=())

    reflection_engine = ReflectionEngine(
        detectors=(DuplicateDetector(), ConflictDetector(), ObsoleteDetector(), GapDetector())
    )

    evolution_engine = EvolutionEngine(
        knowledge_repository=repository,
        evolution_repository=repository,
    )

    detection_pipeline = DetectionPipeline(
        detectors=(),
    )

    event_publisher = EventPublisher()

    reflection_bridge = ReflectionBridge(
        evolution_engine=evolution_engine,
        evolution_repository=repository,
    )

    execution_feedback = ExecutionFeedback()

    learning_coordinator = LearningCoordinator(
        detection=detection_pipeline,
        validation=validation_engine,
        brain=brain_service,
        publisher=event_publisher,
        reflection_engine=reflection_engine,
        reflection_bridge=reflection_bridge,
        execution_feedback=execution_feedback,
    )

    planning_engine = PlanningEngine(strategy=SequentialStrategy())
    planning_use_case = PlanningUseCase(engine=planning_engine)

    execution_engine = ExecutionEngine(
        registry=HandlerRegistry(),
        policy=ExecutionPolicy(),
    )
    execution_use_case = ExecutionUseCase(
        engine=execution_engine,
        planning=planning_use_case,
    )

    learning_use_case = LearningUseCase(coordinator=learning_coordinator)

    execution_learning_mapper = ExecutionLearningMapper()

    reflection_use_case = ReflectionUseCase(
        engine=reflection_engine,
        repository=repository,
    )

    maintenance_service = ReflectionMaintenanceService(
        reflection=reflection_use_case,
    )

    brain_adapter = BrainAdapter(
        session=brain_session,
        mapper=TaskMapper(),
        lifecycle=AdapterLifecycle(),
    )

    workflow = BrainWorkflow(
        session=brain_session,
        planning=planning_use_case,
        execution=execution_use_case,
        learning=learning_use_case,
        mapper=execution_learning_mapper,
    )

    return BrainRuntime(
        adapter=brain_adapter,
        session=brain_session,
        service=brain_service,
        repository=repository,
        validation=validation_engine,
        retrieval=retrieval_engine,
        reflection=reflection_engine,
        evolution=evolution_engine,
        detection=detection_pipeline,
        learning=learning_coordinator,
        publisher=event_publisher,
        workflow=workflow,
        maintenance=maintenance_service,
    )


def create_memory_runtime() -> BrainRuntime:
    repository = InMemoryKnowledgeRepository()
    return _create_common_components(repository)


def create_sqlite_runtime(path: str | None = None) -> BrainRuntime:
    repository = SQLiteKnowledgeRepository(db_path=path)
    return _create_common_components(repository)
