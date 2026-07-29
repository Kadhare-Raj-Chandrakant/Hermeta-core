from datetime import datetime, timezone

import pytest

from brain.pipeline.evidence import Evidence


class TestEvidenceImmutability:
    def test_evidence_is_frozen(self):
        e = Evidence(source_type="conversation", content="test")
        with pytest.raises(AttributeError):
            e.source_type = "other"

    def test_evidence_content_is_frozen(self):
        e = Evidence(source_type="conversation", content="test")
        with pytest.raises(AttributeError):
            e.content = "other"


class TestEvidenceCreation:
    def test_create_with_defaults(self):
        e = Evidence(source_type="conversation", content="test")
        assert e.source_type == "conversation"
        assert e.content == "test"
        assert isinstance(e.detected_at, datetime)

    def test_create_with_explicit_timestamp(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        e = Evidence(source_type="git_commit", content="fix", detected_at=ts)
        assert e.detected_at == ts


class TestEvidenceValidation:
    def test_empty_source_type_raises(self):
        with pytest.raises(ValueError, match="source_type"):
            Evidence(source_type="", content="test")

    def test_whitespace_source_type_raises(self):
        with pytest.raises(ValueError, match="source_type"):
            Evidence(source_type="  ", content="test")

    def test_empty_content_raises(self):
        with pytest.raises(ValueError, match="content"):
            Evidence(source_type="conversation", content="")

    def test_whitespace_content_raises(self):
        with pytest.raises(ValueError, match="content"):
            Evidence(source_type="conversation", content="  ")


class TestEvidenceEquality:
    def test_equal_instances(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        e1 = Evidence(source_type="conversation", content="test", detected_at=ts)
        e2 = Evidence(source_type="conversation", content="test", detected_at=ts)
        assert e1 == e2

    def test_unequal_instances(self):
        ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
        e1 = Evidence(source_type="conversation", content="test", detected_at=ts)
        e2 = Evidence(source_type="git_commit", content="test", detected_at=ts)
        assert e1 != e2
