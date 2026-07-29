import uuid

import pytest

from brain.domain.enums import KnowledgeType
from brain.planning.action import Action
from brain.planning.dependency import Dependency
from brain.planning.strategies.sequential import SequentialStrategy
from brain.planning.strategies.dependency import DependencyStrategy


def make_action(title: str = "Action", **kwargs) -> Action:
    defaults = dict(
        goal_id=uuid.uuid4(),
        title=title,
        description=f"Description for {title}",
    )
    defaults.update(kwargs)
    return Action(**defaults)


def make_dependency(from_id: uuid.UUID, to_id: uuid.UUID, reason: str = "must complete first") -> Dependency:
    return Dependency(from_action_id=from_id, to_action_id=to_id, reason=reason)


class TestSequentialStrategy:
    def setup_method(self):
        self.strategy = SequentialStrategy()

    def test_preserves_order(self):
        a1 = make_action("A")
        a2 = make_action("B")
        a3 = make_action("C")
        result = self.strategy.organize((a1, a2, a3), ())
        assert result[0].title == "A"
        assert result[1].title == "B"
        assert result[2].title == "C"

    def test_empty_input(self):
        result = self.strategy.organize((), ())
        assert result == ()

    def test_single_action(self):
        a = make_action("Only")
        result = self.strategy.organize((a,), ())
        assert len(result) == 1

    def test_ignores_dependencies(self):
        a1 = make_action("A")
        a2 = make_action("B")
        dep = make_dependency(a2.id, a1.id)
        result = self.strategy.organize((a1, a2), (dep,))
        assert result[0].title == "A"
        assert result[1].title == "B"


class TestDependencyStrategy:
    def setup_method(self):
        self.strategy = DependencyStrategy()

    def test_simple_ordering(self):
        a1 = make_action("A")
        a2 = make_action("B")
        dep = make_dependency(a1.id, a2.id)
        result = self.strategy.organize((a1, a2), (dep,))
        assert result[0].title == "A"
        assert result[1].title == "B"

    def test_complex_graph(self):
        a = make_action("A")
        b = make_action("B")
        c = make_action("C")
        d = make_action("D")
        dep_ab = make_dependency(a.id, b.id)
        dep_ac = make_dependency(a.id, c.id)
        dep_bd = make_dependency(b.id, d.id)
        dep_cd = make_dependency(c.id, d.id)
        result = self.strategy.organize((a, b, c, d), (dep_ab, dep_ac, dep_bd, dep_cd))
        titles = [r.title for r in result]
        assert titles[0] == "A"
        assert titles[-1] == "D"
        assert set(titles[1:3]) == {"B", "C"}

    def test_deterministic_output(self):
        a = make_action("A")
        b = make_action("B")
        dep = make_dependency(a.id, b.id)
        r1 = self.strategy.organize((a, b), (dep,))
        r2 = self.strategy.organize((a, b), (dep,))
        assert [r.title for r in r1] == [r.title for r in r2]

    def test_cycle_detection(self):
        a = make_action("A")
        b = make_action("B")
        dep_ab = make_dependency(a.id, b.id)
        dep_ba = make_dependency(b.id, a.id)
        with pytest.raises(ValueError, match="Circular dependency"):
            self.strategy.organize((a, b), (dep_ab, dep_ba))

    def test_empty_input(self):
        result = self.strategy.organize((), ())
        assert result == ()

    def test_no_dependencies(self):
        a1 = make_action("A")
        a2 = make_action("B")
        result = self.strategy.organize((a1, a2), ())
        assert len(result) == 2

    def test_ignores_external_dependencies(self):
        a = make_action("A")
        external_id = uuid.uuid4()
        dep = make_dependency(external_id, a.id)
        result = self.strategy.organize((a,), (dep,))
        assert len(result) == 1

    def test_three_level_chain(self):
        a = make_action("A")
        b = make_action("B")
        c = make_action("C")
        dep_ab = make_dependency(a.id, b.id)
        dep_bc = make_dependency(b.id, c.id)
        result = self.strategy.organize((a, b, c), (dep_ab, dep_bc))
        titles = [r.title for r in result]
        assert titles == ["A", "B", "C"]
