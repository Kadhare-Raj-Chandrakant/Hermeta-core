import uuid
from abc import ABC, abstractmethod

from brain.adapter.models import AdapterContext, AdapterLearning, AdapterTask
from brain.domain.version import KnowledgeVersion


class HermesBrainAdapter(ABC):
    @abstractmethod
    def start_task(self, task: AdapterTask) -> AdapterContext:
        ...

    @abstractmethod
    def learn(self, learning: AdapterLearning) -> KnowledgeVersion:
        ...

    @abstractmethod
    def complete_task(self, task_id: uuid.UUID) -> None:
        ...
