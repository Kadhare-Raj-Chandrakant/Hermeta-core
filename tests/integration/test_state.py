import pytest

from brain.integration.state import IntegrationState, IntegrationStateMachine


class TestIntegrationState:
    def test_idle_value(self) -> None:
        assert IntegrationState.IDLE.value == "idle"

    def test_ready_value(self) -> None:
        assert IntegrationState.READY.value == "ready"

    def test_working_value(self) -> None:
        assert IntegrationState.WORKING.value == "working"

    def test_finished_value(self) -> None:
        assert IntegrationState.FINISHED.value == "finished"

    def test_four_values(self) -> None:
        assert len(IntegrationState) == 4


class TestIntegrationStateMachine:
    def test_initial_state_is_idle(self) -> None:
        machine = IntegrationStateMachine()
        assert machine.state == IntegrationState.IDLE

    def test_idle_to_ready(self) -> None:
        machine = IntegrationStateMachine()
        result = machine.transition(IntegrationState.READY)
        assert result == IntegrationState.READY
        assert machine.state == IntegrationState.READY

    def test_ready_to_working(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        result = machine.transition(IntegrationState.WORKING)
        assert result == IntegrationState.WORKING

    def test_working_to_finished(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        result = machine.transition(IntegrationState.FINISHED)
        assert result == IntegrationState.FINISHED

    def test_finished_to_idle(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        machine.transition(IntegrationState.FINISHED)
        result = machine.transition(IntegrationState.IDLE)
        assert result == IntegrationState.IDLE

    def test_idle_to_working_invalid(self) -> None:
        machine = IntegrationStateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            machine.transition(IntegrationState.WORKING)

    def test_idle_to_finished_invalid(self) -> None:
        machine = IntegrationStateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            machine.transition(IntegrationState.FINISHED)

    def test_ready_to_idle_valid(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        result = machine.transition(IntegrationState.IDLE)
        assert result == IntegrationState.IDLE

    def test_working_to_ready_invalid(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        with pytest.raises(ValueError, match="Invalid transition"):
            machine.transition(IntegrationState.READY)

    def test_working_to_idle_valid(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        result = machine.transition(IntegrationState.IDLE)
        assert result == IntegrationState.IDLE

    def test_finished_to_ready_invalid(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        machine.transition(IntegrationState.FINISHED)
        with pytest.raises(ValueError, match="Invalid transition"):
            machine.transition(IntegrationState.READY)

    def test_reset_returns_to_idle(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        result = machine.reset()
        assert result == IntegrationState.IDLE
        assert machine.state == IntegrationState.IDLE

    def test_full_lifecycle(self) -> None:
        machine = IntegrationStateMachine()
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        machine.transition(IntegrationState.FINISHED)
        machine.transition(IntegrationState.IDLE)
        machine.transition(IntegrationState.READY)
        machine.transition(IntegrationState.WORKING)
        machine.transition(IntegrationState.FINISHED)
        assert machine.state == IntegrationState.FINISHED
