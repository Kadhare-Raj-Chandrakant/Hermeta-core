from abc import ABC, abstractmethod

from brain.events.event import Event


class EventSubscriber(ABC):
    @abstractmethod
    def handle(self, event: Event) -> None:
        ...
