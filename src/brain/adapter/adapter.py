import uuid

from brain.adapter.errors import AdapterError
from brain.adapter.interface import HermesBrainAdapter
from brain.adapter.lifecycle import AdapterLifecycle
from brain.adapter.models import AdapterContext, AdapterLearning, AdapterTask
from brain.adapter.task_mapper import TaskMapper
from brain.application.brain_session import BrainSession
from brain.application.usecases.models import KnowledgeVersionDTO
from brain.domain.enums import KnowledgeType
from brain.pipeline.candidate import KnowledgeCandidate
from brain.pipeline.evidence import Evidence


class BrainAdapter(HermesBrainAdapter):
    def __init__(
        self,
        session: BrainSession,
        mapper: TaskMapper,
        lifecycle: AdapterLifecycle,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._lifecycle = lifecycle

    def start_task(self, task: AdapterTask) -> AdapterContext:
        try:
            domain_task = self._mapper.map(task)
            self._lifecycle.start(task.task_id)
            context = self._session.begin(domain_task)
            return AdapterContext(
                task_id=task.task_id,
                context=context,
            )
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError(f"Internal error during start_task: {e}") from e

    def learn(self, learning: AdapterLearning) -> KnowledgeVersionDTO:
        try:
            self._lifecycle.check_active()
            candidate = KnowledgeCandidate(
                knowledge_type=KnowledgeType[learning.knowledge_type],
                title=learning.title,
                understanding=learning.understanding,
                confidence=learning.confidence,
                evidence_source=Evidence(
                    source_type="observation",
                    content="Submitted via integration layer",
                ),
            )
            return self._session.learn(candidate)
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError(f"Internal error during learn: {e}") from e

    def complete_task(self, task_id: uuid.UUID) -> None:
        try:
            self._lifecycle.complete()
            self._session.complete()
        except AdapterError:
            raise
        except Exception as e:
            raise AdapterError(f"Internal error during complete_task: {e}") from e
