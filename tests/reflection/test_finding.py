import uuid
from datetime import datetime, timezone

import pytest

from brain.reflection.finding import ReflectionFinding
from brain.reflection.type import ReflectionType


def make_finding(**kwargs) -> ReflectionFinding:
    defaults = dict(
        reflection_type=ReflectionType.DUPLICATE,
        affected_versions=(uuid.uuid4(), uuid.uuid4()),
        explanation="Test finding",
        confidence=0.8,
    )
    defaults.update(kwargs)
    return ReflectionFinding(**defaults)


class TestReflectionFindingCreation:
    def test_create_valid(self):
        vid = uuid.uuid4()
        f = ReflectionFinding(
            reflection_type=ReflectionType.CONFLICT,
            affected_versions=(vid,),
            explanation="Test explanation",
            confidence=0.5,
        )
        assert isinstance(f.id, uuid.UUID)
        assert f.reflection_type == ReflectionType.CONFLICT
        assert f.affected_versions == (vid,)
        assert f.explanation == "Test explanation"
        assert f.confidence == 0.5
        assert isinstance(f.created_at, datetime)

    def test_multiple_affected_versions(self):
        vids = (uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
        f = make_finding(affected_versions=vids)
        assert len(f.affected_versions) == 3

    def test_default_confidence(self):
        f = make_finding(confidence=0.0)
        assert f.confidence == 0.0

    def test_max_confidence(self):
        f = make_finding(confidence=1.0)
        assert f.confidence == 1.0


class TestReflectionFindingImmutability:
    def test_frozen(self):
        f = make_finding()
        with pytest.raises(AttributeError):
            f.explanation = "changed"

    def test_affected_versions_frozen(self):
        f = make_finding()
        with pytest.raises(AttributeError):
            f.affected_versions = (uuid.uuid4(),)

    def test_confidence_frozen(self):
        f = make_finding()
        with pytest.raises(AttributeError):
            f.confidence = 0.5


class TestReflectionFindingValidation:
    def test_negative_confidence_raises(self):
        with pytest.raises(ValueError, match="Confidence must be between"):
            make_finding(confidence=-0.1)

    def test_confidence_above_one_raises(self):
        with pytest.raises(ValueError, match="Confidence must be between"):
            make_finding(confidence=1.1)

    def test_empty_explanation_raises(self):
        with pytest.raises(ValueError, match="explanation must not be empty"):
            make_finding(explanation="")

    def test_whitespace_explanation_raises(self):
        with pytest.raises(ValueError, match="explanation must not be empty"):
            make_finding(explanation="  ")

    def test_empty_affected_versions_is_valid(self):
        f = make_finding(affected_versions=())
        assert f.affected_versions == ()

    def test_single_affected_version_is_valid(self):
        f = make_finding(affected_versions=(uuid.uuid4(),))
        assert len(f.affected_versions) == 1
