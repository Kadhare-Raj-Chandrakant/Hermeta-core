import itertools
import logging

from brain.events.event import Event
from brain.events.subscriber import EventSubscriber

logger = logging.getLogger(__name__)

_LOG_SUPPRESSION_BREAKS = 10


class EventPublisher:
    def __init__(self) -> None:
        self._subscribers: list[EventSubscriber] = []
        self._log_suppression_counter = itertools.count()

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
            except Exception as exc:
                # Keep the fault-isolation contract: never stop other subscribers.
                # Log the failure but apply rate limiting to avoid memory blowout under load.
                idx = next(self._log_suppression_counter)
                if idx < _LOG_SUPPRESSION_BREAKS:
                    logger.exception(
                        "Subscriber %s failed handling %s",
                        type(subscriber).__name__,
                        type(event).__name__,
                    )
                elif idx == _LOG_SUPPRESSION_BREAKS:
                    logger.warning(
                        "Suppressed repeated subscriber failures after %d occurrences "
                        "(will resume after next threshold). Last error: %s: %s",
                        _LOG_SUPPRESSION_BREAKS,
                        type(exc).__name__,
                        exc,
                    )
                elif idx % _LOG_SUPPRESSION_BREAKS == 0:
                    logger.warning(
                        "Subscriber failure count=%d (throttled, full traceback suppressed). "
                        "Last error: %s: %s",
                        idx + 1,
                        type(exc).__name__,
                        exc,
                    )

    @property
    def subscribers(self) -> tuple[EventSubscriber, ...]:
        return tuple(self._subscribers)
