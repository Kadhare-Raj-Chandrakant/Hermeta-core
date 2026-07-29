from enum import Enum


class IntegrationState(Enum):
    IDLE = "idle"
    READY = "ready"
    WORKING = "working"
    FINISHED = "finished"


VALID_TRANSITIONS: dict[IntegrationState, set[IntegrationState]] = {
    IntegrationState.IDLE: {IntegrationState.READY},
    IntegrationState.READY: {IntegrationState.WORKING, IntegrationState.IDLE},
    IntegrationState.WORKING: {IntegrationState.FINISHED, IntegrationState.IDLE},
    IntegrationState.FINISHED: {IntegrationState.IDLE},
}


class IntegrationStateMachine:
    def __init__(self) -> None:
        self._state = IntegrationState.IDLE

    @property
    def state(self) -> IntegrationState:
        return self._state

    def transition(self, target: IntegrationState) -> IntegrationState:
        allowed = VALID_TRANSITIONS.get(self._state, set())
        if target not in allowed:
            raise ValueError(
                f"Invalid transition: {self._state.value} -> {target.value}"
            )
        self._state = target
        return self._state

    def reset(self) -> IntegrationState:
        self._state = IntegrationState.IDLE
        return self._state
