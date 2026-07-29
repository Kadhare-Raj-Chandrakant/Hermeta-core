import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.planning.context import PlanningContext


class TestPlanningContextCreation:
    def test_create_empty(self):
        ctx = PlanningContext()
        assert ctx.task_id is None
        assert ctx.knowledge_types == ()
        assert ctx.constraints == ()

    def test_create_with_values(self):
        tid = uuid.uuid4()
        ctx = PlanningContext(
            task_id=tid,
            knowledge_types=(KnowledgeType.ARCHITECTURE, KnowledgeType.DECISION),
            constraints=("must use Python", "no external dependencies"),
        )
        assert ctx.task_id == tid
        assert len(ctx.knowledge_types) == 2
        assert len(ctx.constraints) == 2


class TestPlanningContextImmutability:
    def test_frozen(self):
        ctx = PlanningContext()
        with pytest.raises(AttributeError):
            ctx.task_id = uuid.uuid4()

    def test_knowledge_types_frozen(self):
        ctx = PlanningContext(knowledge_types=(KnowledgeType.RULE,))
        with pytest.raises(AttributeError):
            ctx.knowledge_types = ()

    def test_constraints_frozen(self):
        ctx = PlanningContext(constraints=("c1",))
        with pytest.raises(AttributeError):
            ctx.constraints = ()
