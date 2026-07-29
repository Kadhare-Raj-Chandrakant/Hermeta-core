import pytest

from brain.execution.policy import ExecutionPolicy


class TestExecutionPolicyCreation:
    def test_defaults(self):
        p = ExecutionPolicy()
        assert p.allow_parallel is False
        assert p.stop_on_failure is True
        assert p.require_confirmation is False

    def test_custom(self):
        p = ExecutionPolicy(
            allow_parallel=True,
            stop_on_failure=False,
            require_confirmation=True,
        )
        assert p.allow_parallel is True
        assert p.stop_on_failure is False
        assert p.require_confirmation is True


class TestExecutionPolicyImmutability:
    def test_frozen(self):
        p = ExecutionPolicy()
        with pytest.raises(AttributeError):
            p.stop_on_failure = False
