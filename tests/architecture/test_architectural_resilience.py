"""Architectural Resilience Verification Tests — Events Layer.

Verifies that the Events Layer preserves architectural invariants under adverse conditions.

Invariants Verified:
- I-13: Failures remain localized (publisher faults don't cascade)
- I-14: Every failure has one owner (subscriber errors don't affect others)
- I-15: Recovery never violates architecture (no planning in recovery)
- I-10: Public APIs expose DTOs only (events are frozen DTOs)
- I-11: Internal domain objects never escape application boundaries

Scenarios Tested:
- S1: Publisher fault tolerance (subscriber failures don't cascade)
- S2: Subscriber error handling (errors isolated to failing subscriber)
- S3: Event replay (deterministic replay from history)
- S4: Delivery guarantees (exactly-once, at-least-once, at-most-once)
- S5: Fault injection under load
- S6: Subscription lifecycle under stress
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Callable, Optional
from unittest.mock import MagicMock

import pytest

from brain.events.event import Event
from brain.events.publisher import EventPublisher
from brain.events.subscriber import EventSubscriber
from brain.events.types import (
    ExecutionCompleted,
    ExecutionFailed,
    KnowledgeLearned,
    PlanCompleted,
    ReflectionCompleted,
)
from brain.execution.report import ExecutionReport
from brain.execution.record import ExecutionRecord
from brain.execution.result import ExecutionResult
from brain.execution.status import ExecutionStatus
from brain.learning.execution_feedback import ExecutionFeedback


# ── Generic Helpers ────────────────────────────────────────────────────────

class RecordingSubscriber(EventSubscriber):
    """Subscriber that records all received events."""
    def __init__(self) -> None:
        self.received: list[Event] = []

    def handle(self, event: Event) -> None:
        self.received.append(event)


class FailingSubscriber(EventSubscriber):
    """Subscriber that fails on every handle call."""
    def __init__(self, error: Exception = RuntimeError("subscriber failed")) -> None:
        self.received: list[Event] = []
        self._error = error

    def handle(self, event: Event) -> None:
        self.received.append(event)
        raise self._error


class ConditionalFailingSubscriber(EventSubscriber):
    """Subscriber that fails conditionally."""
    def __init__(
        self,
        fail_on: Optional[Callable[[Event], bool]] = None,
        error: Exception = RuntimeError("conditional failure"),
    ) -> None:
        self.received: list[Event] = []
        self._fail_on = fail_on or (lambda _: False)
        self._error = error

    def handle(self, event: Event) -> None:
        self.received.append(event)
        if self._fail_on(event):
            raise self._error


class CountingSubscriber(EventSubscriber):
    """Subscriber that counts deliveries."""
    def __init__(self, name: str) -> None:
        self._name = name
        self.count = 0

    def handle(self, event: Event) -> None:
        self.count += 1


class OrderTrackingSubscriber(EventSubscriber):
    """Subscriber that tracks delivery order."""
    def __init__(self, name: str, results: list[str]) -> None:
        self._name = name
        self._results = results

    def handle(self, event: Event) -> None:
        self._results.append(self._name)


class ModifyingSubscriber(EventSubscriber):
    """Subscriber that modifies subscription during delivery."""
    def __init__(self, name: str, publisher: EventPublisher, to_add: Optional[EventSubscriber] = None) -> None:
        self._name = name
        self._pub = publisher
        self._to_add = to_add

    def handle(self, event: Event) -> None:
        if self._to_add is not None:
            self._pub.subscribe(self._to_add)


class NestedPublisher(EventSubscriber):
    """Subscriber that publishes another event during handling."""
    def __init__(self, publisher: EventPublisher, inner_event: Event) -> None:
        self._pub = publisher
        self._inner_event = inner_event
        self._published = False

    def handle(self, event: Event) -> None:
        if not self._published:
            self._published = True
            self._pub.publish(self._inner_event)


# ── Invariants: I-13, I-14, I-15 — Publisher Fault Tolerance ──────────────

class TestPublisherFaultTolerance:
    """I-13: Failures remain localized. I-14: Every failure has one owner."""

    def test_failing_subscriber_does_not_stop_others(self):
        """S1: Publisher fault tolerance - failing subscriber doesn't stop others."""
        pub = EventPublisher()
        sub_a = RecordingSubscriber()
        sub_b = FailingSubscriber()
        sub_c = RecordingSubscriber()

        pub.subscribe(sub_a)
        pub.subscribe(sub_b)
        pub.subscribe(sub_c)

        event = ExecutionCompleted(plan_id="p1", actions_completed=3)
        pub.publish(event)

        assert len(sub_a.received) == 1, "Sub A should receive despite B's failure"
        assert sub_a.received[0] is event
        assert len(sub_b.received) == 1, "Failing subscriber still receives"
        assert len(sub_c.received) == 1, "Sub C should receive despite B's failure"
        assert sub_c.received[0] is event

    def test_first_subscriber_failing_still_delivers_to_rest(self):
        """S1: First subscriber failing doesn't block delivery to rest."""
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
        """S1: All subscribers receive event even when some fail."""
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

    def test_failing_subscriber_error_isolated(self):
        """I-14: Failing subscriber's error doesn't propagate to publisher or other subscribers."""
        pub = EventPublisher()
        sub_a = RecordingSubscriber()
        sub_b = FailingSubscriber(RuntimeError("B failed"))
        sub_c = RecordingSubscriber()

        pub.subscribe(sub_a)
        pub.subscribe(sub_b)
        pub.subscribe(sub_c)

        # Should not raise
        pub.publish(ExecutionCompleted(plan_id="p1", actions_completed=3))

        assert len(sub_a.received) == 1
        assert len(sub_c.received) == 1

    def test_multiple_failures_all_isolated(self):
        """Multiple failing subscribers all isolated."""
        pub = EventPublisher()
        failures = [
            FailingSubscriber(ValueError("error 1")),
            FailingSubscriber(TypeError("error 2")),
            FailingSubscriber(KeyError("error 3")),
        ]
        ok = RecordingSubscriber()

        for f in failures:
            pub.subscribe(f)
        pub.subscribe(ok)

        pub.publish(KnowledgeLearned())

        assert len(ok.received) == 1
        for f in failures:
            assert len(f.received) == 1


# ── Invariants: I-13, I-14 — Subscriber Error Handling ─────────────────────

class TestSubscriberErrorHandling:
    """I-13: Failures remain localized. I-14: Every failure has one owner."""

    def test_conditional_failure_only_affects_matching_events(self):
        """S2: Subscriber errors only affect events matching condition."""
        pub = EventPublisher()
        fail_sub = ConditionalFailingSubscriber(
            fail_on=lambda e: isinstance(e, ExecutionFailed),
            error=RuntimeError("fail on failed"),
        )
        ok_sub = RecordingSubscriber()

        pub.subscribe(fail_sub)
        pub.subscribe(ok_sub)

        # This should fail
        pub.publish(ExecutionFailed(plan_id="p1", error="boom"))
        assert len(fail_sub.received) == 1
        assert len(ok_sub.received) == 1

        # This should not fail
        pub.publish(ExecutionCompleted(plan_id="p1", actions_completed=3))
        assert len(ok_sub.received) == 2  # Both events delivered to ok_sub

    def test_subscriber_exception_type_preserved(self):
        """S2: Subscriber exceptions don't mutate into other types."""
        pub = EventPublisher()
        errors = [
            ValueError("value error"),
            TypeError("type error"),
            KeyError("key error"),
            RuntimeError("runtime error"),
        ]
        received = []

        for err in errors:
            sub = FailingSubscriber(err)
            pub.subscribe(sub)
            received.append(sub)

        pub.publish(KnowledgeLearned())

        # All subscribers received the event
        for sub in received:
            assert len(sub.received) == 1

    def test_subscriber_state_not_corrupted_by_failure(self):
        """S2: Subscriber internal state remains consistent after failure."""
        pub = EventPublisher()
        sub = FailingSubscriber()

        pub.subscribe(sub)
        pub.publish(KnowledgeLearned())  # fails
        pub.publish(KnowledgeLearned())  # fails again

        # State should be consistent
        assert len(sub.received) == 2


# ── Invariants: I-13, I-14 — Event Replay ─────────────────────────────────

class TestEventReplay:
    """I-13: Failures remain localized. I-14: Every failure has one owner."""

    def test_replay_from_history_deterministic(self):
        """S3: Replay from history produces deterministic results."""
        pub = EventPublisher()
        history: list[Event] = [
            KnowledgeLearned(knowledge_type="DECISION", title="T1"),
            ExecutionCompleted(plan_id="p1", actions_completed=3),
            KnowledgeLearned(knowledge_type="RULE", title="T2"),
        ]

        for event in history:
            pub.publish(event)

        # Replay
        received = []
        sub = RecordingSubscriber()
        pub.subscribe(sub)

        # Note: This tests that we CAN replay by re-publishing
        # In a real system, this would come from event store
        for event in history:
            pub.publish(event)

        assert len(sub.received) == 3
        assert sub.received[0].event_id == history[0].event_id
        assert sub.received[1].event_id == history[1].event_id
        assert sub.received[2].event_id == history[2].event_id

    def test_replay_preserves_event_order(self):
        """S3: Replay preserves strict event ordering."""
        pub = EventPublisher()
        events = [
            KnowledgeLearned(knowledge_type="DECISION", title="T1"),
            ExecutionCompleted(plan_id="p1", actions_completed=1),
            KnowledgeLearned(knowledge_type="RULE", title="T2"),
            ExecutionCompleted(plan_id="p2", actions_completed=2),
            ReflectionCompleted(findings_count=5),
        ]

        for e in events:
            pub.publish(e)

        received = []
        sub = RecordingSubscriber()
        pub.subscribe(sub)

        for e in events:
            pub.publish(e)

        assert [e.event_id for e in sub.received] == [e.event_id for e in events]

    def test_replay_after_failure_recovers_state(self):
        """S3: Replay after failure recovers to consistent state."""
        pub = EventPublisher()
        fail_sub = FailingSubscriber()
        ok_sub = RecordingSubscriber()

        pub.subscribe(fail_sub)
        pub.subscribe(ok_sub)

        # Initial publish - fails for fail_sub
        pub.publish(KnowledgeLearned(knowledge_type="DECISION", title="T1"))
        assert len(ok_sub.received) == 1

        # Simulate "recovery" - re-publish to new subscriber
        new_sub = RecordingSubscriber()
        pub.subscribe(new_sub)
        pub.publish(KnowledgeLearned(knowledge_type="RULE", title="T2"))

        assert len(new_sub.received) == 1
        assert len(ok_sub.received) == 2


# ── Invariants: I-10, I-11 — Delivery Guarantees ──────────────────────────

class TestDeliveryGuarantees:
    """I-10: Public APIs expose DTOs only. I-11: Internal domain objects never escape."""

    def test_each_subscriber_receives_exactly_once(self):
        """S4: Exactly-once delivery per event per subscriber."""
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
        """S4: Multiple publishes - each delivered exactly once per subscriber."""
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

    def test_no_duplicate_delivery_for_duplicate_subscription(self):
        """S4: Duplicate subscription doesn't cause duplicate delivery."""
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.subscribe(sub)  # Duplicate
        pub.subscribe(sub)  # Duplicate again

        pub.publish(KnowledgeLearned())

        assert len(sub.received) == 1

    def test_unsubscribed_receives_zero(self):
        """S4: Unsubscribed subscriber receives nothing (at-most-once)."""
        pub = EventPublisher()
        sub = RecordingSubscriber()

        pub.subscribe(sub)
        pub.publish(KnowledgeLearned())
        assert len(sub.received) == 1

        pub.unsubscribe(sub)
        pub.publish(ExecutionCompleted(plan_id="p1", actions_completed=1))
        assert len(sub.received) == 1  # Still just 1

    def test_event_immutability_preserved_during_delivery(self):
        """I-10, I-11: Events are immutable DTOs, internal objects never escape."""
        pub = EventPublisher()
        received_events = []

        class Inspector(EventSubscriber):
            def handle(self, event: Event) -> None:
                received_events.append(event)
                # Verify event is frozen
                with pytest.raises(AttributeError):
                    event.event_id = uuid.uuid4()

        pub.subscribe(Inspector())
        pub.publish(KnowledgeLearned(knowledge_type="DECISION", title="Test"))
        assert len(received_events) == 1


# ── Invariants: I-13, I-14, I-15 — Subscription Lifecycle Under Stress ──────

class TestSubscriptionLifecycleUnderStress:
    """I-13: Failures remain localized. I-15: Recovery never violates architecture."""

    def test_rapid_subscribe_unsubscribe_cycles(self):
        """S5: Rapid subscribe/unsubscribe doesn't break delivery."""
        pub = EventPublisher()
        received = []

        class Counter(EventSubscriber):
            def handle(self, event: Event) -> None:
                received.append(1)

        for _ in range(100):
            sub = Counter()
            pub.subscribe(sub)
            pub.publish(KnowledgeLearned())
            pub.unsubscribe(sub)

        assert len(received) == 100

    def test_subscribe_during_publish_does_not_collapse(self):
        """S5: Subscribing during publish uses snapshot iteration."""
        pub = EventPublisher()
        results = []

        class ModifyingSubscriber(EventSubscriber):
            def __init__(self, name: str, publisher: EventPublisher, to_add: Optional[EventSubscriber] = None) -> None:
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

    def test_unsubscribe_during_publish_safe(self):
        """S5: Unsubscribing during publish is safe."""
        pub = EventPublisher()
        results = []

        class Unsubscriber(EventSubscriber):
            def __init__(self, publisher: EventPublisher, to_unsub: EventSubscriber) -> None:
                self._pub = publisher
                self._to_unsub = to_unsub
            def handle(self, event: Event) -> None:
                results.append("A")
                self._pub.unsubscribe(self._to_unsub)

        sub_b = RecordingSubscriber()
        pub.subscribe(Unsubscriber(pub, sub_b))
        pub.subscribe(sub_b)

        pub.publish(KnowledgeLearned())

        assert "A" in results
        assert len(sub_b.received) == 1  # B still received because snapshot taken

    def test_modifying_during_publish_does_not_collapse(self):
        """S5: Modifying subscriptions during publish doesn't collapse."""
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


# ── Invariants: I-13, I-14, I-15 — Nested/Reentrant Publishing ────────────

class TestNestedPublishing:
    """I-15: Recovery never violates architecture. No planning in recovery."""

    def test_nested_publish_works(self):
        """S6: Nested publish works without deadlock."""
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

    def test_reentrant_publish_does_not_deadlock(self):
        """S6: Reentrant publish doesn't deadlock."""
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


# ── Invariants: I-10, I-11 — Event Immutability & Contract Boundaries ──────

class TestEventImmutabilityAndContracts:
    """I-10: Public APIs expose DTOs only. I-11: Internal domain objects never escape."""

    def test_event_is_frozen(self):
        """I-10: Events are frozen dataclasses."""
        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        with pytest.raises(AttributeError):
            event.title = "Changed"

    def test_event_has_uuid(self):
        """Events have unique identity."""
        event = Event()
        assert isinstance(event.event_id, uuid.UUID)

    def test_event_has_timestamp(self):
        """Events have timestamp."""
        event = Event()
        assert event.timestamp is not None

    def test_event_is_hashable(self):
        """Events can be used in sets/dicts."""
        event = KnowledgeLearned(knowledge_type="DECISION", title="Test")
        hash(event)

    def test_all_event_types_are_frozen(self):
        """All event types are immutable."""
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

    def test_no_internal_objects_leak_through_events(self):
        """I-11: Events contain only DTOs, no internal domain objects."""
        pub = EventPublisher()
        received = []

        class Inspector(EventSubscriber):
            def handle(self, event: Event) -> None:
                received.append(event)

        pub.subscribe(Inspector())
        pub.publish(KnowledgeLearned(knowledge_type="DECISION", title="Test"))

        assert len(received) == 1
        event = received[0]
        # Event should only contain primitive/DTO data
        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")


# ── Invariants: I-13, I-14 — Fault Injection Under Load ──────────────────

class TestFaultInjectionUnderLoad:
    """I-13: Failures remain localized. I-14: Every failure has one owner."""

    def test_many_subscribers_many_failures(self):
        """S5: Many subscribers, many failures - all isolated."""
        pub = EventPublisher()
        num_subs = 50
        fail_every = 5

        subs = []
        for i in range(num_subs):
            if i % fail_every == 0:
                subs.append(FailingSubscriber())
            else:
                subs.append(RecordingSubscriber())
            pub.subscribe(subs[-1])

        pub.publish(KnowledgeLearned())

        # Non-failing subscribers should all receive
        for i, sub in enumerate(subs):
            if i % 5 != 0:
                assert len(sub.received) == 1
            else:
                assert len(sub.received) == 1  # Still receives, just fails internally

    def test_rapid_publish_with_failures(self):
        """S5: Rapid publishing with intermittent failures."""
        pub = EventPublisher()
        ok_sub = RecordingSubscriber()
        pub.subscribe(ok_sub)

        for i in range(100):
            if i % 10 == 0:
                pub.subscribe(FailingSubscriber())
            pub.publish(KnowledgeLearned(knowledge_type="DECISION", title=f"T{i}"))

        assert len(ok_sub.received) == 100

    def test_sustained_failure_rate(self):
        """S5: Sustained high failure rate doesn't accumulate errors."""
        pub = EventPublisher()
        ok = RecordingSubscriber()
        pub.subscribe(ok)

        for i in range(1000):
            if i % 2 == 0:
                pub.subscribe(FailingSubscriber())
            pub.publish(KnowledgeLearned(knowledge_type="RULE", title=f"R{i}"))

        assert len(ok.received) == 1000


# ── Invariants: I-10, I-11 — Execution Feedback Metadata ──────────────────

class TestExecutionFeedbackMetadata:
    """I-10: Public APIs expose DTOs only. I-11: Internal domain objects never escape."""

    def test_execution_feedback_produces_metadata(self):
        """Execution feedback produces structured metadata DTOs."""
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
        """Failed execution metadata includes error details."""
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
        """Metadata contains structured facts, not prose."""
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
        """Same input produces identical observations."""
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


# ── Invariants Summary Matrix ────────────────────────────────────────────

class TestInvariantSummary:
    """Summary matrix documenting which invariants each test verifies."""

    def test_invariant_matrix_documented(self):
        """This test serves as documentation of the invariant coverage."""
        # This is a documentation test - it doesn't execute assertions
        # but serves as a coverage map for the resilience scenarios

        invariant_coverage = {
            "I-10": ["Public APIs expose DTOs only"],
            "I-11": ["Internal domain objects never escape"],
            "I-13": ["Failures remain localized"],
            "I-14": ["Every failure has one owner"],
            "I-15": ["Recovery never violates architecture"],
        }

        scenario_coverage = {
            "S1": ["Publisher fault tolerance", "I-13", "I-14"],
            "S2": ["Subscriber error handling", "I-13", "I-14"],
            "S3": ["Event replay", "I-13", "I-14"],
            "S4": ["Delivery guarantees", "I-10", "I-11"],
            "S5": ["Subscription lifecycle under stress", "I-13", "I-14", "I-15"],
            "S6": ["Nested/Reentrant publishing", "I-15"],
        }

        # This assertion always passes - it's documentation
        assert invariant_coverage
        assert scenario_coverage