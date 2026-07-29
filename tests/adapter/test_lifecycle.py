import uuid

import pytest

from brain.adapter.errors import AdapterNotReadyError
from brain.adapter.lifecycle import AdapterLifecycle, AdapterLifecycleState, AdapterState


class TestAdapterLifecycle:
    def test_initial_state_is_none(self) -> None:
        lifecycle = AdapterLifecycle()
        assert lifecycle.state is None

    def test_start_sets_active(self) -> None:
        lifecycle = AdapterLifecycle()
        task_id = uuid.uuid4()
        state = lifecycle.start(task_id)
        assert state.state == AdapterLifecycleState.ACTIVE
        assert state.task_id == task_id
        assert state.started_at is not None
        assert state.completed_at is None

    def test_complete_sets_completed(self) -> None:
        lifecycle = AdapterLifecycle()
        task_id = uuid.uuid4()
        lifecycle.start(task_id)
        state = lifecycle.complete()
        assert state.state == AdapterLifecycleState.COMPLETED
        assert state.completed_at is not None

    def test_double_start_rejected(self) -> None:
        lifecycle = AdapterLifecycle()
        lifecycle.start(uuid.uuid4())
        with pytest.raises(AdapterNotReadyError, match="Session already active"):
            lifecycle.start(uuid.uuid4())

    def test_complete_before_start_rejected(self) -> None:
        lifecycle = AdapterLifecycle()
        with pytest.raises(AdapterNotReadyError, match="No active session to complete"):
            lifecycle.complete()

    def test_learn_before_start_rejected(self) -> None:
        lifecycle = AdapterLifecycle()
        with pytest.raises(AdapterNotReadyError, match="No active session"):
            lifecycle.check_active()

    def test_check_active_when_active(self) -> None:
        lifecycle = AdapterLifecycle()
        lifecycle.start(uuid.uuid4())
        lifecycle.check_active()

    def test_start_after_complete_works(self) -> None:
        lifecycle = AdapterLifecycle()
        lifecycle.start(uuid.uuid4())
        lifecycle.complete()
        state = lifecycle.start(uuid.uuid4())
        assert state.state == AdapterLifecycleState.ACTIVE

    def test_adapter_state_is_frozen(self) -> None:
        state = AdapterState(
            task_id=uuid.uuid4(),
            state=AdapterLifecycleState.CREATED,
        )
        with pytest.raises(AttributeError):
            state.state = AdapterLifecycleState.ACTIVE  # type: ignore[misc]

    def test_adapter_state_fields(self) -> None:
        task_id = uuid.uuid4()
        state = AdapterState(
            task_id=task_id,
            state=AdapterLifecycleState.ACTIVE,
            started_at=None,
            completed_at=None,
        )
        assert state.task_id == task_id
        assert state.state == AdapterLifecycleState.ACTIVE
        assert state.started_at is None
        assert state.completed_at is None

    def test_lifecycle_preserves_task_id(self) -> None:
        lifecycle = AdapterLifecycle()
        task_id = uuid.uuid4()
        lifecycle.start(task_id)
        state = lifecycle.complete()
        assert state.task_id == task_id
