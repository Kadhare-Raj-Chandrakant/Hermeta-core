from brain.reflection.type import ReflectionType


class TestReflectionTypeValues:
    def test_duplicate(self):
        assert ReflectionType.DUPLICATE.value == "duplicate"

    def test_conflict(self):
        assert ReflectionType.CONFLICT.value == "conflict"

    def test_obsolete(self):
        assert ReflectionType.OBSOLETE.value == "obsolete"

    def test_gap(self):
        assert ReflectionType.GAP.value == "gap"

    def test_four_values(self):
        assert len(ReflectionType) == 4


class TestReflectionTypeImmutability:
    def test_cannot_instantiate_new_members(self):
        with pytest.raises(ValueError):
            ReflectionType("custom")

    def test_members_are_hashable(self):
        assert hash(ReflectionType.DUPLICATE) == hash(ReflectionType.DUPLICATE)

    def test_members_are_usable_as_dict_keys(self):
        d = {ReflectionType.DUPLICATE: "dup", ReflectionType.GAP: "gap"}
        assert d[ReflectionType.DUPLICATE] == "dup"


import pytest
