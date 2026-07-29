from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType
from brain.pipeline.evidence import Evidence
from brain.pipeline.events import KnowledgeEvent


def make_evidence() -> Evidence:
    return Evidence(source_type="conversation", content="We decided to use Redis")


def make_event(
    event_type: KnowledgeType = KnowledgeType.DECISION,
    description: str = "Use Redis for caching",
) -> KnowledgeEvent:
    return KnowledgeEvent(
        event_type=event_type,
        description=description,
        evidence_source=make_evidence(),
    )


class TestKnowledgeEventImmutability:
    def test_event_is_frozen(self):
        e = make_event()
        with pytest.raises(AttributeError):
            e.description = "other"

    def test_event_type_is_frozen(self):
        e = make_event()
        with pytest.raises(AttributeError):
            e.event_type = KnowledgeType.BUG


class TestKnowledgeEventCreation:
    def test_create_with_defaults(self):
        e = make_event()
        assert e.event_type == KnowledgeType.DECISION
        assert e.description == "Use Redis for caching"
        assert isinstance(e.detected_at, datetime)

    def test_create_with_explicit_timestamp(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        e = KnowledgeEvent(
            event_type=KnowledgeType.BUG,
            description="Found a bug",
            evidence_source=make_evidence(),
            detected_at=ts,
        )
        assert e.detected_at == ts


class TestKnowledgeEventValidation:
    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="description"):
            KnowledgeEvent(
                event_type=KnowledgeType.DECISION,
                description="",
                evidence_source=make_evidence(),
            )

    def test_whitespace_description_raises(self):
        with pytest.raises(ValueError, match="description"):
            KnowledgeEvent(
                event_type=KnowledgeType.DECISION,
                description="  ",
                evidence_source=make_evidence(),
            )


class TestKnowledgeEventEquality:
    def test_equal_instances(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        ev = make_evidence()
        e1 = KnowledgeEvent(
            event_type=KnowledgeType.DECISION,
            description="Use Redis",
            evidence_source=ev,
            detected_at=ts,
        )
        e2 = KnowledgeEvent(
            event_type=KnowledgeType.DECISION,
            description="Use Redis",
            evidence_source=ev,
            detected_at=ts,
        )
        assert e1 == e2

    def test_unequal_instances(self):
        ev = make_evidence()
        e1 = KnowledgeEvent(
            event_type=KnowledgeType.DECISION,
            description="Use Redis",
            evidence_source=ev,
        )
        e2 = KnowledgeEvent(
            event_type=KnowledgeType.BUG,
            description="Use Redis",
            evidence_source=ev,
        )
        assert e1 != e2
