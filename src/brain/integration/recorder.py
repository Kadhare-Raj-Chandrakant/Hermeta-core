from brain.integration.events import IntegrationEvent


class EventRecorder:
    def __init__(self) -> None:
        self._events: list[IntegrationEvent] = []

    def record(self, event: IntegrationEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> tuple[IntegrationEvent, ...]:
        return tuple(self._events)

    def clear(self) -> None:
        self._events.clear()
