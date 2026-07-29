import uuid
from datetime import datetime, timezone

import pytest

from brain.domain.enums import KnowledgeType
from brain.planning.action import Action, ActionStatus


def make_action(**kwargs) -> Action:
    defaults = dict(
        goal_id=uuid.uuid4(),
        title="Test Action",
        description="A test action description",
    )
    defaults.update(kwargs)
    return Action(**defaults)


class TestActionCreation:
    def test_create_valid(self):
        a = make_action()
        assert isinstance(a.id, uuid.UUID)
        assert isinstance(a.goal_id, uuid.UUID)
        assert a.title == "Test Action"
        assert a.description == "A test action description"
        assert a.required_knowledge == ()
        assert a.dependencies == ()
        assert a.status == ActionStatus.PENDING

    def test_with_knowledge_types(self):
        a = make_action(required_knowledge=(KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION))
        assert len(a.required_knowledge) == 2

    def test_with_dependencies(self):
        dep_id = uuid.uuid4()
        a = make_action(dependencies=(dep_id,))
        assert len(a.dependencies) == 1
        assert a.dependencies[0] == dep_id


class TestActionImmutability:
    def test_frozen(self):
        a = make_action()
        with pytest.raises(AttributeError):
            a.title = "changed"

    def test_dependencies_frozen(self):
        a = make_action()
        with pytest.raises(AttributeError):
            a.dependencies = ()

    def test_required_knowledge_frozen(self):
        a = make_action()
        with pytest.raises(AttributeError):
            a.required_knowledge = ()


class TestActionValidation:
    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="title must not be empty"):
            make_action(title="")

    def test_whitespace_title_raises(self):
        with pytest.raises(ValueError, match="title must not be empty"):
            make_action(title="  ")

    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match="description must not be empty"):
            make_action(description="")
