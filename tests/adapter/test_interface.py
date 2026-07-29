import pytest

from brain.adapter.interface import HermesBrainAdapter


class TestHermesBrainAdapter:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            HermesBrainAdapter()  # type: ignore[abstract]

    def test_has_start_task_method(self) -> None:
        assert hasattr(HermesBrainAdapter, "start_task")

    def test_has_learn_method(self) -> None:
        assert hasattr(HermesBrainAdapter, "learn")

    def test_has_complete_task_method(self) -> None:
        assert hasattr(HermesBrainAdapter, "complete_task")
