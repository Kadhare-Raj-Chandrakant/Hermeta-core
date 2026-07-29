import uuid

import pytest

from brain.events.event import Event


class TestEventBase:
    def test_create_event(self):
        event = Event()
        assert isinstance(event.event_id, uuid.UUID)
        assert event.timestamp is not None

    def test_events_are_immutable(self):
        event = Event()
        with pytest.raises(AttributeError):
            event.event_id = uuid.uuid4()

    def test_events_have_unique_ids(self):
        e1 = Event()
        e2 = Event()
        assert e1.event_id != e2.event_id

    def test_events_are_ordered_by_creation(self):
        e1 = Event()
        e2 = Event()
        assert e1.timestamp <= e2.timestamp

    def test_events_are_equal_by_id(self):
        id_ = uuid.uuid4()
        e1 = Event(event_id=id_)
        e2 = Event(event_id=id_)
        assert e1 == e2
