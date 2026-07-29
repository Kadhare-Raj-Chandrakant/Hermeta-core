from datetime import datetime, timezone

import pytest

from brain.detection.observation import Observation


class TestObservationCreation:
    def test_create_with_defaults(self):
        obs = Observation(source_type="conversation", content="test content")
        assert obs.source_type == "conversation"
        assert obs.content == "test content"
        assert obs.metadata == ()
        assert obs.observed_at is not None

    def test_create_with_explicit_timestamp(self):
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        obs = Observation(source_type="git", content="commit abc", observed_at=ts)
        assert obs.observed_at == ts

    def test_create_with_metadata(self):
        obs = Observation(
            source_type="ide",
            content="file changed",
            metadata=(("file", "main.py"), ("action", "edit")),
        )
        assert obs.metadata == (("file", "main.py"), ("action", "edit"))


class TestObservationValidation:
    def test_empty_source_type_raises(self):
        with pytest.raises(ValueError, match="source_type"):
            Observation(source_type="", content="test")

    def test_whitespace_source_type_raises(self):
        with pytest.raises(ValueError, match="source_type"):
            Observation(source_type="  ", content="test")

    def test_empty_content_raises(self):
        with pytest.raises(ValueError, match="content"):
            Observation(source_type="conversation", content="")

    def test_whitespace_content_raises(self):
        with pytest.raises(ValueError, match="content"):
            Observation(source_type="conversation", content="  ")


class TestObservationImmutability:
    def test_observation_is_frozen(self):
        obs = Observation(source_type="test", content="test")
        with pytest.raises(AttributeError):
            obs.source_type = "changed"

    def test_metadata_is_immutable(self):
        obs = Observation(
            source_type="test",
            content="test",
            metadata=(("key", "value"),),
        )
        with pytest.raises(AttributeError):
            obs.metadata = ()


class TestObservationEquality:
    def test_equal_instances(self):
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        obs1 = Observation(source_type="test", content="test", observed_at=ts)
        obs2 = Observation(source_type="test", content="test", observed_at=ts)
        assert obs1 == obs2

    def test_unequal_instances(self):
        obs1 = Observation(source_type="test", content="one")
        obs2 = Observation(source_type="test", content="two")
        assert obs1 != obs2
