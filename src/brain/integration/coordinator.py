import uuid
from dataclasses import dataclass
from typing import Optional

from brain.adapter.adapter import BrainAdapter
from brain.adapter.errors import AdapterError
from brain.adapter.models import AdapterLearning, AdapterTask
from brain.domain.task import TaskType
from brain.integration.errors import IntegrationError
from brain.integration.events import (
    ContextPrepared,
    ContextUnavailable,
    IntegrationEvent,
    KnowledgeLearned,
    LearningFailed,
    TaskCompleted,
    TaskStarted,
)
from brain.integration.models import IntegrationContext, IntegrationLearning, IntegrationSection, IntegrationTask
from brain.integration.recorder import EventRecorder
from brain.integration.state import IntegrationState, IntegrationStateMachine


@dataclass(frozen=True)
class IntegrationStatus:
    state: str
    tasks_started: int
    tasks_completed: int
    learn_operations: int
    failures: int


class SessionCoordinator:
    def __init__(self, adapter: BrainAdapter, recorder: Optional[EventRecorder] = None) -> None:
        self._adapter = adapter
        self._recorder = recorder
        self._machine = IntegrationStateMachine()
        self._tasks_started: int = 0
        self._tasks_completed: int = 0
        self._learn_operations: int = 0
        self._failures: int = 0

    @property
    def state(self) -> IntegrationState:
        return self._machine.state

    def status(self) -> IntegrationStatus:
        return IntegrationStatus(
            state=self._machine.state.value,
            tasks_started=self._tasks_started,
            tasks_completed=self._tasks_completed,
            learn_operations=self._learn_operations,
            failures=self._failures,
        )

    def _emit(self, event: IntegrationEvent) -> None:
        if self._recorder is not None:
            self._recorder.record(event)

    def start_task(self, task: IntegrationTask) -> IntegrationContext:
        self._emit(TaskStarted(task_id=task.task_id))
        self._machine.transition(IntegrationState.READY)
        try:
            adapter_task = AdapterTask(
                task_id=task.task_id,
                task_type=TaskType[task.task_type],
                objective=task.objective,
                project=task.project,
                component=task.component,
                metadata=task.metadata,
            )
            adapter_context = self._adapter.start_task(adapter_task)
            sections = tuple(
                IntegrationSection(
                    section_type=s.section_type,
                    title=s.title,
                    content=tuple(v.title for v in s.content),
                )
                for s in adapter_context.context.sections
            )
            self._machine.transition(IntegrationState.WORKING)
            self._tasks_started += 1
            context = IntegrationContext(
                task_id=task.task_id,
                sections=sections,
            )
            self._emit(ContextPrepared(
                task_id=task.task_id,
                section_count=len(context.sections),
            ))
            return context
        except AdapterError as e:
            self._machine.reset()
            self._failures += 1
            self._emit(ContextUnavailable(task_id=task.task_id, reason=str(e)))
            raise IntegrationError(str(e)) from e
        except Exception as e:
            self._machine.reset()
            self._failures += 1
            self._emit(ContextUnavailable(task_id=task.task_id, reason=str(e)))
            raise IntegrationError(f"Failed to start task: {e}") from e

    def learn(self, learning: IntegrationLearning) -> None:
        try:
            adapter_learning = AdapterLearning(
                task_id=learning.task_id,
                knowledge_type=learning.knowledge_type,
                title=learning.title,
                understanding=learning.understanding,
                confidence=learning.confidence,
            )
            self._adapter.learn(adapter_learning)
            self._learn_operations += 1
            self._emit(KnowledgeLearned(
                task_id=learning.task_id,
                knowledge_type=learning.knowledge_type,
                title=learning.title,
            ))
        except AdapterError as e:
            self._machine.reset()
            self._failures += 1
            self._emit(LearningFailed(task_id=learning.task_id, reason=str(e)))
            raise IntegrationError(str(e)) from e
        except Exception as e:
            self._machine.reset()
            self._failures += 1
            self._emit(LearningFailed(task_id=learning.task_id, reason=str(e)))
            raise IntegrationError(f"Failed to learn: {e}") from e

    def complete_task(self, task_id: uuid.UUID) -> None:
        self._machine.transition(IntegrationState.FINISHED)
        try:
            self._adapter.complete_task(task_id)
            self._machine.transition(IntegrationState.IDLE)
            self._tasks_completed += 1
            self._emit(TaskCompleted(task_id=task_id))
        except AdapterError as e:
            self._machine.reset()
            self._failures += 1
            raise IntegrationError(str(e)) from e
        except Exception as e:
            self._machine.reset()
            self._failures += 1
            raise IntegrationError(f"Failed to complete task: {e}") from e
