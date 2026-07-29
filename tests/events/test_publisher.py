import pytest

from brain.events.event import Event
from brain.events.publisher import EventPublisher
from brain.events.subscriber import EventSubscriber
from brain.events.types import KnowledgeLearned


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.received: list[Event] = []

    def handle(self, event: Event) -> None:
        self.received.append(event)


class TestEventPublisher:
    def test_create_publisher(self):
        pub = EventPublisher()
        assert len(pub.subscribers) == 0

    def test_subscribe(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()
        pub.subscribe(sub)
        assert len(pub.subscribers) == 1
        assert sub in pub.subscribers

    def test_publish_to_subscriber(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()
        pub.subscribe(sub)

        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        pub.publish(event)

        assert len(sub.received) == 1
        assert sub.received[0] is event

    def test_publish_to_multiple_subscribers(self):
        pub = EventPublisher()
        sub1 = RecordingSubscriber()
        sub2 = RecordingSubscriber()
        pub.subscribe(sub1)
        pub.subscribe(sub2)

        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        pub.publish(event)

        assert len(sub1.received) == 1
        assert len(sub2.received) == 1

    def test_publish_order_is_deterministic(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()
        pub.subscribe(sub)

        e1 = KnowledgeLearned(knowledge_type="DECISION", title="First")
        e2 = KnowledgeLearned(knowledge_type="RULE", title="Second")
        pub.publish(e1)
        pub.publish(e2)

        assert sub.received[0] is e1
        assert sub.received[1] is e2

    def test_publish_with_no_subscribers(self):
        pub = EventPublisher()
        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        pub.publish(event)

    def test_multiple_subscribers_independent(self):
        pub = EventPublisher()
        sub1 = RecordingSubscriber()
        sub2 = RecordingSubscriber()
        pub.subscribe(sub1)

        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        pub.publish(event)

        assert len(sub1.received) == 1
        assert len(sub2.received) == 0
