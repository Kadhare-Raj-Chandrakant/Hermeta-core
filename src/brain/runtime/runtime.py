from dataclasses import dataclass

from brain.adapter.adapter import BrainAdapter
from brain.application.brain_service import BrainService
from brain.application.brain_session import BrainSession
from brain.application.maintenance.service import ReflectionMaintenanceService
from brain.application.workflow.workflow import BrainWorkflow
from brain.detection.pipeline import DetectionPipeline
from brain.evolution.evolution import EvolutionEngine
from brain.events.publisher import EventPublisher
from brain.learning.coordinator import LearningCoordinator
from brain.reflection.engine import ReflectionEngine
from brain.repositories.base import KnowledgeRepository
from brain.retrieval.engine import RetrievalTriggerEngine
from brain.validation.engine import ValidationEngine


@dataclass(frozen=True)
class BrainRuntime:
    adapter: BrainAdapter
    session: BrainSession
    service: BrainService
    repository: KnowledgeRepository
    validation: ValidationEngine
    retrieval: RetrievalTriggerEngine
    reflection: ReflectionEngine
    evolution: EvolutionEngine
    detection: DetectionPipeline
    learning: LearningCoordinator
    publisher: EventPublisher
    workflow: BrainWorkflow
    maintenance: ReflectionMaintenanceService
