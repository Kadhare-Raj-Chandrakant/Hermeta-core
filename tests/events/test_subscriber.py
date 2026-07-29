import pytest

from brain.events.subscriber import EventSubscriber
from brain.events.event import Event


class TestEventSubscriber:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            EventSubscriber()

    def test_implements_interface(self):
        class TestSub(EventSubscriber):
            def handle(self, event: Event) -> None:
                pass

        sub = TestSub()
        assert isinstance(sub, EventSubscriber)
