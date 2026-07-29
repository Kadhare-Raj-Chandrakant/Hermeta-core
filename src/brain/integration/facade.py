import uuid

from brain.adapter.adapter import BrainAdapter
from brain.integration.coordinator import IntegrationStatus, SessionCoordinator
from brain.integration.errors import IntegrationError
from brain.integration.events import IntegrationEvent
from brain.integration.models import IntegrationContext, IntegrationLearning, IntegrationTask
from brain.integration.recorder import EventRecorder
from brain.integration.state import IntegrationState


class IntegrationLayer:
    def __init__(self, adapter: BrainAdapter) -> None:
        self._recorder = EventRecorder()
        self._coordinator = SessionCoordinator(adapter, recorder=self._recorder)

    @property
    def state(self) -> IntegrationState:
        return self._coordinator.state

    @property
    def events(self) -> tuple[IntegrationEvent, ...]:
        return self._recorder.events

    def status(self) -> IntegrationStatus:
        return self._coordinator.status()

    def start_task(self, task: IntegrationTask) -> IntegrationContext:
        return self._coordinator.start_task(task)

    def learn(self, learning: IntegrationLearning) -> None:
        self._coordinator.learn(learning)

    def complete_task(self, task_id: uuid.UUID) -> None:
        self._coordinator.complete_task(task_id)
