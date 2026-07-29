import pytest
from brain.evolution.transition_type import TransitionType


class TestTransitionTypeValues:
    def test_update_exists(self):
        assert TransitionType.UPDATE.value == "update"

    def test_refinement_exists(self):
        assert TransitionType.REFINEMENT.value == "refinement"

    def test_supersedes_exists(self):
        assert TransitionType.SUPERSEDES.value == "supersedes"

    def test_extends_exists(self):
        assert TransitionType.EXTENDS.value == "extends"

    def test_contradicts_exists(self):
        assert TransitionType.CONTRADICTS.value == "contradicts"

    def test_five_values(self):
        assert len(TransitionType) == 5


class TestTransitionTypeImmutability:
    def test_is_enum(self):
        assert issubclass(TransitionType, type(TransitionType.UPDATE))

    def test_members_are独一无b(self):
        values = [t.value for t in TransitionType]
        assert len(values) == len(set(values))
