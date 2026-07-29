from brain.events.event import Event
from brain.events.subscriber import EventSubscriber


class EventPublisher:
    def __init__(self) -> None:
        self._subscribers: list[EventSubscriber] = []

    def subscribe(self, subscriber: EventSubscriber) -> None:
        for existing in self._subscribers:
            if existing is subscriber:
                return
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        self._subscribers = [s for s in self._subscribers if s is not subscriber]

    def publish(self, event: Event) -> None:
        for subscriber in tuple(self._subscribers):
            try:
                subscriber.handle(event)
            except Exception:
                pass

    @property
    def subscribers(self) -> tuple[EventSubscriber, ...]:
        return tuple(self._subscribers)
