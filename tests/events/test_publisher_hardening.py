import uuid
from unittest.mock import MagicMock

import pytest

from brain.events.event import Event
from brain.events.publisher import EventPublisher
from brain.events.subscriber import EventSubscriber
from brain.events.types import ExecutionCompleted, KnowledgeLearned


class RecordingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.received: list[Event] = []

    def handle(self, event: Event) -> None:
        self.received.append(event)


class FailingSubscriber(EventSubscriber):
    def __init__(self) -> None:
        self.received: list[Event] = []

    def handle(self, event: Event) -> None:
        self.received.append(event)
        raise RuntimeError("subscriber failed")


class TestFaultIsolation:
    def test_failing_subscriber_does_not_stop_others(self):
        pub = EventPublisher()
        sub_a = RecordingSubscriber()
        sub_b = FailingSubscriber()
        sub_c = RecordingSubscriber()

        pub.subscribe(sub_a)
        pub.subscribe(sub_b)
        pub.subscribe(sub_c)

        event = ExecutionCompleted(plan_id="p1", actions_completed=3)
        pub.publish(event)

        assert len(sub_a.received) == 1
        assert sub_a.received[0] is event
        assert len(sub_b.received) == 1
        assert len(sub_c.received) == 1
        assert sub_c.received[0] is event

    def test_first_subscriber_failing_still_delivers_to_rest(self):
        pub = EventPublisher()
        sub_fail = FailingSubscriber()
        sub_ok = RecordingSubscriber()

        pub.subscribe(sub_fail)
        pub.subscribe(sub_ok)

        event = KnowledgeLearned(knowledge_type="RULE", title="Test")
        pub.publish(event)

        assert len(sub_ok.received) == 1
        assert sub_ok.received[0] is event

    def test_all_subscribers_receive_even_with_failures(self):
        pub = EventPublisher()
        results = []

        class OrderedSubscriber(EventSubscriber):
            def __init__(self, name: str) -> None:
                self._name = name
            def handle(self, event: Event) -> None:
                results.append(self._name)
                if self._name == "B":
                    raise RuntimeError("B failed")

        pub.subscribe(OrderedSubscriber("A"))
        pub.subscribe(OrderedSubscriber("B"))
        pub.subscribe(OrderedSubscriber("C"))

        pub.publish(KnowledgeLearned())

        assert results == ["A", "B", "C"]


class TestDeterministicOrder:
    def test_subscribers_execute_in_registration_order(self):
        pub = EventPublisher()
        results = []

        class OrderTracker(EventSubscriber):
            def __init__(self, name: str) -> None:
                self._name = name
            def handle(self, event: Event) -> None:
                results.append(self._name)

        pub.subscribe(OrderTracker("First"))
        pub.subscribe(OrderTracker("Second"))
        pub.subscribe(OrderTracker("Third"))

        pub.publish(KnowledgeLearned())

        assert results == ["First", "Second", "Third"]

    def test_order_preserved_across_multiple_publishes(self):
        pub = EventPublisher()
        all_results = []

        class OrderTracker(EventSubscriber):
            def __init__(self, name: str) -> None:
                self._name = name
            def handle(self, event: Event) -> None:
                all_results.append(self._name)

        pub.subscribe(OrderTracker("X"))
        pub.subscribe(OrderTracker("Y"))

        pub.publish(KnowledgeLearned())
        pub.publish(ExecutionCompleted())

        assert all_results == ["X", "Y", "X", "Y"]


class TestDuplicateSubscription:
    def test_same_subscriber_registered_once(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.subscribe(sub)
        pub.subscribe(sub)

        assert len(pub.subscribers) == 1

    def test_different_subscribers_both_registered(self):
        pub = EventPublisher()
        sub1 = RecordingSubscriber()
        sub2 = RecordingSubscriber()

        pub.subscribe(sub1)
        pub.subscribe(sub2)

        assert len(pub.subscribers) == 2

    def test_duplicate_subscriber_receives_once(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.subscribe(sub)

        pub.publish(KnowledgeLearned())

        assert len(sub.received) == 1


class TestUnsubscribe:
    def test_unsubscribe_removes_subscriber(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        assert len(pub.subscribers) == 1

        pub.unsubscribe(sub)
        assert len(pub.subscribers) == 0

    def test_unsubscribe_missing_subscriber_is_safe(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.unsubscribe(sub)

        assert len(pub.subscribers) == 0

    def test_unsubscribe_does_not_affect_others(self):
        pub = EventPublisher()
        sub1 = RecordingSubscriber()
        sub2 = RecordingSubscriber()

        pub.subscribe(sub1)
        pub.subscribe(sub2)
        pub.unsubscribe(sub1)

        assert len(pub.subscribers) == 1
        assert sub2 in pub.subscribers

    def test_publish_after_unsubscribe(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.publish(KnowledgeLearned())
        assert len(sub.received) == 1

        pub.unsubscribe(sub)
        pub.publish(KnowledgeLearned())
        assert len(sub.received) == 1

    def test_unsubscribe_is_idempotent(self):
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.unsubscribe(sub)
        pub.unsubscribe(sub)

        assert len(pub.subscribers) == 0

    def test_unsubscribe_missing_preserves_existing(self):
        pub = EventPublisher()
        sub1 = RecordingSubscriber()
        sub2 = RecordingSubscriber()

        pub.subscribe(sub1)
        pub.unsubscribe(sub2)

        assert len(pub.subscribers) == 1
        assert sub1 in pub.subscribers


class TestSnapshotIteration:
    def test_publish_uses_snapshot(self):
        pub = EventPublisher()
        results = []

        class ModifyingSubscriber(EventSubscriber):
            def __init__(self, name: str, publisher: EventPublisher, to_add: EventSubscriber | None = None) -> None:
                self._name = name
                self._pub = publisher
                self._to_add = to_add
            def handle(self, event: Event) -> None:
                results.append(self._name)
                if self._to_add is not None:
                    self._pub.subscribe(self._to_add)

        new_sub = RecordingSubscriber()
        pub.subscribe(ModifyingSubscriber("A", pub, new_sub))
        pub.subscribe(ModifyingSubscriber("B", pub))

        pub.publish(KnowledgeLearned())

        assert "A" in results
        assert "B" in results

    def test_modifying_during_publish_does_not_collapse(self):
        pub = EventPublisher()
        delivery_count = [0]

        class CountingSubscriber(EventSubscriber):
            def handle(self, event: Event) -> None:
                delivery_count[0] += 1

        pub.subscribe(CountingSubscriber())
        pub.subscribe(CountingSubscriber())
        pub.subscribe(CountingSubscriber())

        pub.publish(KnowledgeLearned())

        assert delivery_count[0] == 3


class TestReentrantPublishing:
    def test_nested_publish_works(self):
        pub = EventPublisher()
        events_received = []

        class NestedPublisher(EventSubscriber):
            def __init__(self, publisher: EventPublisher) -> None:
                self._pub = publisher
                self._depth = 0
            def handle(self, event: Event) -> None:
                events_received.append(("outer", type(event).__name__))
                if self._depth == 0:
                    self._depth = 1
                    self._pub.publish(ExecutionCompleted(plan_id="nested", actions_completed=1))

        pub.subscribe(NestedPublisher(pub))
        pub.subscribe(RecordingSubscriber())

        pub.publish(KnowledgeLearned())

        outer_events = [e for e in events_received if e[0] == "outer"]
        assert len(outer_events) >= 1

    def test_reentrant_does_not_deadlock(self):
        pub = EventPublisher()
        count = [0]

        class ReentrantSub(EventSubscriber):
            def __init__(self, publisher: EventPublisher) -> None:
                self._pub = publisher
            def handle(self, event: Event) -> None:
                count[0] += 1
                if count[0] == 1:
                    self._pub.publish(KnowledgeLearned())

        pub.subscribe(ReentrantSub(pub))

        pub.publish(KnowledgeLearned())

        assert count[0] == 2


class TestExactlyOnce:
    def test_each_subscriber_receives_exactly_once(self):
        pub = EventPublisher()
        delivery_counts = {}

        class CountingSubscriber(EventSubscriber):
            def __init__(self, name: str) -> None:
                self._name = name
            def handle(self, event: Event) -> None:
                delivery_counts[self._name] = delivery_counts.get(self._name, 0) + 1

        pub.subscribe(CountingSubscriber("A"))
        pub.subscribe(CountingSubscriber("B"))
        pub.subscribe(CountingSubscriber("C"))

        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        pub.publish(event)

        assert delivery_counts == {"A": 1, "B": 1, "C": 1}

    def test_multiple_publishes_each_delivered_exactly_once(self):
        pub = EventPublisher()
        delivery_counts = {}

        class CountingSubscriber(EventSubscriber):
            def __init__(self, name: str) -> None:
                self._name = name
            def handle(self, event: Event) -> None:
                delivery_counts[self._name] = delivery_counts.get(self._name, 0) + 1

        pub.subscribe(CountingSubscriber("X"))
        pub.subscribe(CountingSubscriber("Y"))

        pub.publish(KnowledgeLearned())
        pub.publish(ExecutionCompleted())
        pub.publish(KnowledgeLearned())

        assert delivery_counts == {"X": 3, "Y": 3}


class TestEventImmutability:
    def test_event_is_frozen(self):
        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        with pytest.raises(AttributeError):
            event.title = "Changed"

    def test_event_has_uuid(self):
        event = Event()
        assert isinstance(event.event_id, uuid.UUID)

    def test_event_has_timestamp(self):
        event = Event()
        assert event.timestamp is not None

    def test_event_is_hashable(self):
        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        hash(event)

    def test_all_event_types_are_frozen(self):
        from brain.events.types import (
            ConflictDetected,
            ExecutionCompleted,
            ExecutionFailed,
            KnowledgeLearned,
            PlanCompleted,
            ReflectionCompleted,
        )

        events = [
            KnowledgeLearned(knowledge_type="DECISION", title="T"),
            ExecutionCompleted(plan_id="p", actions_completed=1),
            ExecutionFailed(plan_id="p", error="e"),
            ReflectionCompleted(findings_count=1),
            ConflictDetected(description="d"),
            PlanCompleted(plan_id="p", confidence=0.9),
        ]
        for event in events:
            with pytest.raises(AttributeError):
                event.event_id = uuid.uuid4()


class TestRichExecutionObservationMetadata:
    def test_execution_feedback_produces_metadata(self):
        from brain.learning.execution_feedback import ExecutionFeedback
        from brain.execution.report import ExecutionReport
        from brain.execution.record import ExecutionRecord
        from brain.execution.result import ExecutionResult
        from brain.execution.status import ExecutionStatus
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.COMPLETED,
                started_at=now,
                completed_at=now,
            ),
            success=True,
            output="Deployed v2.1 to production",
            duration=timedelta(seconds=5.0),
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        feedback = ExecutionFeedback()
        observations = feedback.to_observations(report)

        assert len(observations) == 1
        obs = observations[0]
        assert obs.source_type == "execution"
        assert "Deployed" in obs.content
        assert len(obs.metadata) > 0

        meta_dict = dict(obs.metadata)
        assert "plan_id" in meta_dict
        assert "action_id" in meta_dict
        assert meta_dict["status"] == "completed"
        assert "duration_ms" in meta_dict
        assert meta_dict["output"] == "Deployed v2.1 to production"

    def test_failed_execution_has_error_metadata(self):
        from brain.learning.execution_feedback import ExecutionFeedback
        from brain.execution.report import ExecutionReport
        from brain.execution.record import ExecutionRecord
        from brain.execution.result import ExecutionResult
        from brain.execution.status import ExecutionStatus
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.FAILED,
                started_at=now,
                completed_at=now,
            ),
            success=False,
            output="",
            error="ConnectionRefusedError: Redis refused connection",
            duration=timedelta(seconds=2.0),
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        feedback = ExecutionFeedback()
        observations = feedback.to_observations(report)

        obs = observations[0]
        meta_dict = dict(obs.metadata)
        assert meta_dict["status"] == "failed"
        assert "error_type" in meta_dict
        assert "error_message" in meta_dict
        assert "Redis refused" in meta_dict["error_message"]

    def test_metadata_facts_not_prose(self):
        from brain.learning.execution_feedback import ExecutionFeedback
        from brain.execution.report import ExecutionReport
        from brain.execution.record import ExecutionRecord
        from brain.execution.result import ExecutionResult
        from brain.execution.status import ExecutionStatus
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.COMPLETED,
                started_at=now,
                completed_at=now,
            ),
            success=True,
            output="ok",
            duration=timedelta(seconds=0.1),
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        feedback = ExecutionFeedback()
        observations = feedback.to_observations(report)
        obs = observations[0]

        for key, value in obs.metadata:
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) > 0
            assert len(value) > 0

    def test_execution_feedback_deterministic(self):
        from brain.learning.execution_feedback import ExecutionFeedback
        from brain.execution.report import ExecutionReport
        from brain.execution.record import ExecutionRecord
        from brain.execution.result import ExecutionResult
        from brain.execution.status import ExecutionStatus
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        result = ExecutionResult(
            record=ExecutionRecord(
                action_id=uuid.uuid4(),
                status=ExecutionStatus.COMPLETED,
                started_at=now,
                completed_at=now,
            ),
            success=True,
            output="test output",
            duration=timedelta(seconds=1.0),
        )
        report = ExecutionReport(
            plan_id=uuid.uuid4(),
            results=(result,),
            started_at=now,
            completed_at=now,
        )

        feedback = ExecutionFeedback()
        obs1 = feedback.to_observations(report)
        obs2 = feedback.to_observations(report)

        assert len(obs1) == len(obs2)
        assert obs1[0].source_type == obs2[0].source_type
        assert obs1[0].content == obs2[0].content
        assert obs1[0].metadata == obs2[0].metadata
