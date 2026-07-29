import uuid

import pytest

from brain.application.usecases.evolution import EvolutionUseCase
from brain.application.usecases.models import (
    EvolutionRequest,
    EvolutionSummary,
    ExecutionMetrics,
    PlanningMetrics,
)
from brain.application.usecases.unit_of_work import EvolutionUnitOfWork
from brain.evolution.evolution import EvolutionEngine
from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_operation import EvolutionOperation
from brain.evolution.evolution_plan import EvolutionPlan
from brain.evolution.evolution_record import (
    EvolutionRecord,
    ExecutionFailureRecord,
    OptimisticConcurrencyError,
)
from brain.evolution.executor import EvolutionExecutor
from brain.evolution.planning import EvolutionPlanner
from brain.evolution.transition_type import TransitionType
from brain.repositories.memory import InMemoryKnowledgeRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_planner() -> EvolutionPlanner:
    from unittest.mock import MagicMock
    return MagicMock(spec=EvolutionPlanner)


def _make_request(
    targets: tuple[uuid.UUID, ...] = (),
    context: str = "",
) -> EvolutionRequest:
    return EvolutionRequest(targets=targets, context=context)


def _make_context(
    previous_failures: tuple[tuple[uuid.UUID, ...], ...] = (),
    attempt_count: int = 0,
    quarantined_targets: tuple[uuid.UUID, ...] = (),
    planning_policy: str = "default",
) -> EvolutionContext:
    return EvolutionContext(
        previous_failures=previous_failures,
        attempt_count=attempt_count,
        quarantined_targets=quarantined_targets,
        planning_policy=planning_policy,
    )


def _make_version(
    identity_id: uuid.UUID,
    version_number: int = 1,
) -> object:
    from brain.domain.enums import KnowledgeType, LifecycleState
    from brain.domain.version import KnowledgeVersion
    return KnowledgeVersion(
        identity_id=identity_id,
        version_number=version_number,
        knowledge_type=KnowledgeType.DISCOVERY,
        title="test",
        understanding="test",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
    )


# ---------------------------------------------------------------------------
# EvolutionOperation
# ---------------------------------------------------------------------------

class TestEvolutionOperation:
    def test_construction(self):
        tid = uuid.uuid4()
        op = EvolutionOperation(
            target_id=tid,
            expected_version_id=tid,
            transition_type=TransitionType.UPDATE,
            reason="test",
        )
        assert op.target_id == tid
        assert op.expected_version_id == tid
        assert op.transition_type == TransitionType.UPDATE

    def test_frozen(self):
        op = EvolutionOperation(
            target_id=uuid.uuid4(),
            expected_version_id=uuid.uuid4(),
            transition_type=TransitionType.SUPERSEDES,
            reason="frozen check",
        )
        with pytest.raises(AttributeError):
            op.target_id = uuid.uuid4()

    def test_equality(self):
        tid = uuid.uuid4()
        op1 = EvolutionOperation(tid, tid, TransitionType.UPDATE, "same")
        op2 = EvolutionOperation(tid, tid, TransitionType.UPDATE, "same")
        assert op1 == op2


# ---------------------------------------------------------------------------
# EvolutionPlan
# ---------------------------------------------------------------------------

class TestEvolutionPlanConstruction:
    def test_empty_plan(self):
        plan = EvolutionPlan(operations=(), affected_targets=())
        assert plan.operations == ()
        assert plan.affected_targets == ()

    def test_with_operations(self):
        tid = uuid.uuid4()
        op = EvolutionOperation(tid, tid, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(
            operations=(op,),
            affected_targets=(tid,),
            metadata=(("category", "test"),),
        )
        assert len(plan.operations) == 1
        assert plan.operations[0] is op
        assert plan.affected_targets == (tid,)

    def test_frozen(self):
        plan = EvolutionPlan(operations=(), affected_targets=())
        with pytest.raises(AttributeError):
            plan.operations = ()


class TestEvolutionPlanExpectedVersions:
    def test_expected_version_in_operation(self):
        tid = uuid.uuid4()
        evid = uuid.uuid4()
        op = EvolutionOperation(
            target_id=tid,
            expected_version_id=evid,
            transition_type=TransitionType.UPDATE,
            reason="optimistic concurrency",
        )
        assert op.expected_version_id == evid
        assert op.target_id == tid
        assert op.expected_version_id != op.target_id

    def test_expected_versions_preserved_in_plan(self):
        tid1, tid2 = uuid.uuid4(), uuid.uuid4()
        ev1, ev2 = uuid.uuid4(), uuid.uuid4()
        ops = (
            EvolutionOperation(tid1, ev1, TransitionType.UPDATE, "op1"),
            EvolutionOperation(tid2, ev2, TransitionType.REFINEMENT, "op2"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=(tid1, tid2))
        assert plan.operations[0].expected_version_id == ev1
        assert plan.operations[1].expected_version_id == ev2


# ---------------------------------------------------------------------------
# EvolutionContext
# ---------------------------------------------------------------------------

class TestEvolutionContextConstruction:
    def test_default_construction(self):
        ctx = _make_context()
        assert ctx.previous_failures == ()
        assert ctx.attempt_count == 0
        assert ctx.quarantined_targets == ()
        assert ctx.planning_policy == "default"

    def test_with_values(self):
        tid = uuid.uuid4()
        ctx = _make_context(
            previous_failures=((tid,),),
            attempt_count=2,
            quarantined_targets=(tid,),
            planning_policy="skip_failures",
        )
        assert ctx.previous_failures == ((tid,),)
        assert ctx.attempt_count == 2
        assert ctx.quarantined_targets == (tid,)
        assert ctx.planning_policy == "skip_failures"

    def test_frozen(self):
        ctx = _make_context()
        with pytest.raises(AttributeError):
            ctx.attempt_count = 5

    def test_equality(self):
        tid = uuid.uuid4()
        c1 = EvolutionContext(
            previous_failures=((tid,),),
            attempt_count=1,
            quarantined_targets=(tid,),
            planning_policy="strict",
        )
        c2 = EvolutionContext(
            previous_failures=((tid,),),
            attempt_count=1,
            quarantined_targets=(tid,),
            planning_policy="strict",
        )
        assert c1 == c2

    def test_inequality_on_attempt_count(self):
        c1 = _make_context(attempt_count=1)
        c2 = _make_context(attempt_count=2)
        assert c1 != c2

    def test_inequality_on_quarantine(self):
        t = uuid.uuid4()
        c1 = _make_context(quarantined_targets=(t,))
        c2 = _make_context(quarantined_targets=())
        assert c1 != c2


# ---------------------------------------------------------------------------
# EvolutionRecord
# ---------------------------------------------------------------------------

class TestEvolutionRecord:
    def test_success_construction(self):
        pid = uuid.uuid4()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        record = EvolutionRecord(
            plan_identity=pid,
            executed_at=now,
            success=True,
            operations_count=3,
            affected_targets=(uuid.uuid4(),),
            reason="execution_success",
        )
        assert record.plan_identity == pid
        assert record.success is True
        assert record.operations_count == 3

    def test_frozen(self):
        record = EvolutionRecord(
            plan_identity=uuid.uuid4(),
            executed_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            success=True,
            operations_count=0,
            affected_targets=(),
        )
        with pytest.raises(AttributeError):
            record.success = False


class TestExecutionFailureRecord:
    def test_failure_construction(self):
        pid = uuid.uuid4()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        record = ExecutionFailureRecord(
            plan_identity=pid,
            executed_at=now,
            failure_reason="OCC mismatch",
            failed_operation_index=0,
            operations_count=3,
            failure_type="optimistic_concurrency",
        )
        assert record.plan_identity == pid
        assert record.failure_type == "optimistic_concurrency"
        assert record.failed_operation_index == 0

    def test_frozen(self):
        from datetime import datetime, timezone
        record = ExecutionFailureRecord(
            plan_identity=uuid.uuid4(),
            executed_at=datetime.now(timezone.utc),
            failure_reason="fail",
            failed_operation_index=0,
            operations_count=1,
            failure_type="test",
        )
        with pytest.raises(AttributeError):
            record.failure_reason = "changed"


class TestOptimisticConcurrencyError:
    def test_construction(self):
        tid = uuid.uuid4()
        evid = uuid.uuid4()
        acid = uuid.uuid4()
        err = OptimisticConcurrencyError(
            operation_index=0,
            target_id=tid,
            expected_version_id=evid,
            actual_version_id=acid,
        )
        assert err.operation_index == 0
        assert err.target_id == tid
        assert err.expected_version_id == evid
        assert err.actual_version_id == acid
        assert "expected version" in str(err)


# ---------------------------------------------------------------------------
# EvolutionUseCase
# ---------------------------------------------------------------------------

def _make_repo_use_case(
    planner: EvolutionPlanner | None = None,
    executor: EvolutionExecutor | None = None,
) -> EvolutionUseCase:
    repo = InMemoryKnowledgeRepository()
    if planner is None:
        planner = _make_planner()
    if executor is None:
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
    return EvolutionUseCase(
        planner=planner,
        executor=executor,
        knowledge_repository=repo,
        evolution_repository=repo,
    )


def _make_mock_use_case(
    planner: EvolutionPlanner | None = None,
    executor: object | None = None,
) -> EvolutionUseCase:
    repo = InMemoryKnowledgeRepository()
    if planner is None:
        planner = _make_planner()
    if executor is None:
        from unittest.mock import MagicMock
        executor = MagicMock(spec=EvolutionExecutor)
    return EvolutionUseCase(
        planner=planner,
        executor=executor,
        knowledge_repository=repo,
        evolution_repository=repo,
    )


class TestUseCaseConstruction:
    def test_constructor(self):
        repo = InMemoryKnowledgeRepository()
        planner = _make_planner()
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        use_case = EvolutionUseCase(
            planner=planner,
            executor=executor,
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        assert use_case.planner is planner
        assert use_case.executor is executor
        assert use_case.knowledge_repository is repo
        assert use_case.evolution_repository is repo

    def test_frozen(self):
        repo = InMemoryKnowledgeRepository()
        use_case = _make_repo_use_case()
        with pytest.raises(AttributeError):
            use_case.planner = None


def _make_success_record(ops_count: int = 0) -> EvolutionRecord:
    from datetime import datetime, timezone
    return EvolutionRecord(
        plan_identity=uuid.uuid4(),
        executed_at=datetime.now(timezone.utc),
        success=True,
        operations_count=ops_count,
        affected_targets=(),
    )


class TestUseCaseExecutePlanningOnly:
    def test_returns_evolution_summary(self):
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(operations=(), affected_targets=())
        use_case = _make_mock_use_case(planner=planner)
        use_case.executor.execute.return_value = _make_success_record()
        result = use_case.execute(_make_request(), _make_context())
        assert isinstance(result, EvolutionSummary)

    def test_delegates_to_planner_plan(self):
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(operations=(), affected_targets=())
        use_case = _make_mock_use_case(planner=planner)
        use_case.executor.execute.return_value = _make_success_record()
        req = _make_request(targets=(uuid.uuid4(),), context="duplicate")
        ctx = _make_context()
        use_case.execute(req, ctx)
        planner.plan.assert_called_once_with(
            targets=req.targets,
            category=req.context,
            context=ctx,
        )

    def test_summary_started_completed(self):
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(operations=(), affected_targets=())
        use_case = _make_mock_use_case(planner=planner)
        use_case.executor.execute.return_value = _make_success_record()
        result = use_case.execute(_make_request(), _make_context())
        assert result.evolution_started is True
        assert result.evolution_completed is True

    def test_summary_planning_metrics_preserved(self):
        planner = _make_planner()
        tid = uuid.uuid4()
        ops = (
            EvolutionOperation(tid, tid, TransitionType.UPDATE, "op1"),
            EvolutionOperation(tid, tid, TransitionType.REFINEMENT, "op2"),
        )
        planner.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid,),
            metadata=(("category", "test"), ("quarantined_skipped", "0")),
        )
        use_case = _make_mock_use_case(planner=planner)
        use_case.executor.execute.return_value = _make_success_record(ops_count=2)
        result = use_case.execute(_make_request(), _make_context())
        assert result.planning.planned_operations_count == 2
        assert result.planning.affected_targets_count == 1

    def test_handles_planning_failure(self):
        planner = _make_planner()
        planner.plan.side_effect = RuntimeError("plan failed")
        use_case = _make_mock_use_case(planner=planner)
        with pytest.raises(RuntimeError, match="plan failed"):
            use_case.execute(_make_request(), _make_context())


class TestUseCaseExecuteExecutionMetrics:
    def test_execution_metrics_on_success(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        tid = identity.id
        ops = (
            EvolutionOperation(
                target_id=tid,
                expected_version_id=v1.version_id,
                transition_type=TransitionType.UPDATE,
                reason="test",
            ),
        )
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid,),
        )
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        use_case = EvolutionUseCase(
            planner=planner,
            executor=executor,
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        result = use_case.execute(_make_request(), _make_context())
        assert result.evolution_success is True
        assert result.execution.executed_operations == 1
        assert result.execution.successful_operations == 1
        assert result.execution.failed_operations == 0
        assert result.execution.rolled_back is False
        assert result.execution.optimistic_conflicts == 0
        assert result.planning.planned_operations_count == 1

    def test_execution_metrics_on_occ_failure(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        tid = identity.id
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(
                target_id=tid,
                expected_version_id=wrong_vid,
                transition_type=TransitionType.UPDATE,
                reason="test",
            ),
        )
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid,),
        )
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        use_case = EvolutionUseCase(
            planner=planner,
            executor=executor,
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        result = use_case.execute(_make_request(), _make_context())
        assert result.evolution_success is False
        assert result.execution.executed_operations == 0
        assert result.execution.successful_operations == 0
        assert result.execution.rolled_back is True
        assert result.execution.optimistic_conflicts == 1
        assert result.planning.planned_operations_count == 1

    def test_execution_metrics_coexist_with_planning(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        tid = identity.id
        ops = (
            EvolutionOperation(
                target_id=tid,
                expected_version_id=v1.version_id,
                transition_type=TransitionType.UPDATE,
                reason="test",
            ),
        )
        planner = _make_planner()
        planner.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid,),
            metadata=(("category", "obsolete"), ("quarantined_skipped", "0")),
        )
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        use_case = EvolutionUseCase(
            planner=planner,
            executor=executor,
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        result = use_case.execute(_make_request(), _make_context())
        assert result.planning.planned_operations_count == 1
        assert result.execution.executed_operations == 1
        assert result.planning.quarantined_skipped == 0


# ---------------------------------------------------------------------------
# EvolutionPlanner.plan() — pure integration tests
# ---------------------------------------------------------------------------

class TestPlannerPlan:
    def test_plan_returns_evolution_plan(self):
        planner = EvolutionPlanner()
        plan = planner.plan(targets=(), category="inspect", context=_make_context())
        assert isinstance(plan, EvolutionPlan)

    def test_empty_targets_empty_plan(self):
        planner = EvolutionPlanner()
        plan = planner.plan(targets=(), category="duplicate", context=_make_context())
        assert plan.operations == ()
        assert plan.affected_targets == ()

    def test_duplicate_plans_supersedes(self):
        planner = EvolutionPlanner()
        a, b = uuid.uuid4(), uuid.uuid4()
        plan = planner.plan(targets=(a, b), category="duplicate", context=_make_context())
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.SUPERSEDES

    def test_conflict_plans_refinement(self):
        planner = EvolutionPlanner()
        a, b = uuid.uuid4(), uuid.uuid4()
        plan = planner.plan(targets=(a, b), category="conflict", context=_make_context())
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.REFINEMENT

    def test_obsolete_plans_update(self):
        planner = EvolutionPlanner()
        a = uuid.uuid4()
        plan = planner.plan(targets=(a,), category="obsolete", context=_make_context())
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.UPDATE

    def test_identical_input_identical_plan(self):
        planner = EvolutionPlanner()
        a, b = uuid.uuid4(), uuid.uuid4()
        targets = (a, b)
        ctx = _make_context()
        assert planner.plan(targets, "conflict", ctx) == planner.plan(targets, "conflict", ctx)


class TestPlannerPlanContextRespectsQuarantine:
    def test_quarantined_targets_skipped(self):
        planner = EvolutionPlanner()
        a, b = uuid.uuid4(), uuid.uuid4()
        ctx = _make_context(quarantined_targets=(a,))
        plan = planner.plan(targets=(a, b), category="duplicate", context=ctx)
        assert len(plan.operations) == 0


# ---------------------------------------------------------------------------
# EvolutionExecutor — execution responsibility
# ---------------------------------------------------------------------------

class TestEvolutionExecutorConstruction:
    def test_requires_repos(self):
        repo = InMemoryKnowledgeRepository()
        executor = EvolutionExecutor(
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        assert executor is not None


class TestEvolutionExecutorExecutesOperations:
    def test_execute_single_update(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        tid = identity.id
        op = EvolutionOperation(tid, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(tid,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        record = executor.execute(plan, _make_context())
        assert record.success is True
        assert record.operations_count == 1

    def test_execute_preserves_operation_order(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        ops = tuple(
            EvolutionOperation(v.identity_id, v.version_id, TransitionType.UPDATE, f"op{i}")
            for i, v in enumerate(versions)
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(v.identity_id for v in versions))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        executor.execute(plan, _make_context())
        for i, v in enumerate(versions):
            current = repo.get_latest_version(v.identity_id)
            assert current.version_id == v.version_id

    def test_executor_never_creates_plans(self):
        repo = InMemoryKnowledgeRepository()
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        assert not hasattr(executor, "plan")
        assert not hasattr(executor, "planner")

    def test_executor_never_mutates_plan(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        ops_before = plan.operations
        executor.execute(plan, _make_context())
        assert plan.operations == ops_before

    def test_executor_creates_transition(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        executor.execute(plan, _make_context())
        transitions = repo.get_transitions_for_version(v1.version_id)
        assert len(transitions) == 1
        assert str(transitions[0].reason).startswith("test")


# ---------------------------------------------------------------------------
# Optimistic Concurrency
# ---------------------------------------------------------------------------

class TestOptimisticConcurrency:
    def test_matching_version_succeeds(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        record = executor.execute(plan, _make_context())
        assert record.success is True

    def test_stale_version_aborts(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        wrong_vid = uuid.uuid4()
        op = EvolutionOperation(identity.id, wrong_vid, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        with pytest.raises(OptimisticConcurrencyError):
            executor.execute(plan, _make_context())

    def test_no_mutation_after_stale_detection(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        wrong_vid = uuid.uuid4()
        op = EvolutionOperation(identity.id, wrong_vid, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        with pytest.raises(OptimisticConcurrencyError):
            executor.execute(plan, _make_context())
        current = repo.get_latest_version(identity.id)
        assert current.version_id == v1.version_id
        assert current.lifecycle_state.value == "active"

    def test_occ_checked_before_any_write(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(2)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(ids[0].id, versions[0].version_id, TransitionType.UPDATE, "ok"),
            EvolutionOperation(ids[1].id, wrong_vid, TransitionType.UPDATE, "bad"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        with pytest.raises(OptimisticConcurrencyError):
            executor.execute(plan, _make_context())
        current0 = repo.get_latest_version(ids[0].id)
        assert current0.lifecycle_state.value == "active"

    def test_all_operations_checked_before_write(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(ids[0].id, versions[0].version_id, TransitionType.UPDATE, "op1"),
            EvolutionOperation(ids[1].id, versions[1].version_id, TransitionType.UPDATE, "op2"),
            EvolutionOperation(ids[2].id, wrong_vid, TransitionType.UPDATE, "op3"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        with pytest.raises(OptimisticConcurrencyError):
            executor.execute(plan, _make_context())
        for id_ in ids:
            current = repo.get_latest_version(id_.id)
            assert current.lifecycle_state.value == "active"


# ---------------------------------------------------------------------------
# Transaction / UnitOfWork
# ---------------------------------------------------------------------------

class TestUnitOfWorkConstruction:
    def test_create_uow(self):
        uow = EvolutionUnitOfWork()
        assert uow is not None

    def test_begin_commit(self):
        uow = EvolutionUnitOfWork()
        uow.begin()
        uow.commit()
        assert uow._active is False

    def test_begin_rollback(self):
        uow = EvolutionUnitOfWork()
        uow.begin()
        uow.rollback()
        assert uow._active is False

    def test_commit_without_begin_raises(self):
        uow = EvolutionUnitOfWork()
        with pytest.raises(RuntimeError, match="No active transaction"):
            uow.commit()

    def test_rollback_without_begin_raises(self):
        uow = EvolutionUnitOfWork()
        with pytest.raises(RuntimeError, match="No active transaction"):
            uow.rollback()

    def test_double_begin_raises(self):
        uow = EvolutionUnitOfWork()
        uow.begin()
        with pytest.raises(RuntimeError, match="already active"):
            uow.begin()


class TestTransactionCommitOnSuccess:
    def test_state_changes_persisted_after_commit(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        snapshot = repo.snapshot()

        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except Exception:
            uow.rollback()
            raise

        current = repo.get_latest_version(identity.id)
        assert current.lifecycle_state.value == "archived"


class TestTransactionRollbackOnFailure:
    def test_rollback_on_occ_restores_state(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        wrong_vid = uuid.uuid4()
        snapshot = repo.snapshot()

        op = EvolutionOperation(identity.id, wrong_vid, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except OptimisticConcurrencyError:
            uow.rollback()

        current = repo.get_latest_version(identity.id)
        assert current.version_id == v1.version_id
        assert current.lifecycle_state.value == "active"

    def test_rollback_on_repository_exception(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)

        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            repo.replace_version = lambda x: (_ for _ in ()).throw(RuntimeError("repo fail"))
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except Exception:
            uow.rollback()

        current = repo.get_latest_version(identity.id)
        assert current.lifecycle_state.value == "active"

    def test_rollback_on_concurrency_failure(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        wrong_vid = uuid.uuid4()

        op = EvolutionOperation(identity.id, wrong_vid, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except OptimisticConcurrencyError:
            uow.rollback()

        current = repo.get_latest_version(identity.id)
        assert current.lifecycle_state.value == "active"
        records = repo.get_execution_records()
        assert len(records) == 0


# ---------------------------------------------------------------------------
# Atomicity (all-or-nothing)
# ---------------------------------------------------------------------------

class TestAtomicity:
    def test_failure_on_first_op_unchanged_state(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(ids[0].id, wrong_vid, TransitionType.UPDATE, "fail"),
            EvolutionOperation(ids[1].id, versions[1].version_id, TransitionType.UPDATE, "ok2"),
            EvolutionOperation(ids[2].id, versions[2].version_id, TransitionType.UPDATE, "ok3"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except OptimisticConcurrencyError:
            uow.rollback()

        for id_ in ids:
            current = repo.get_latest_version(id_.id)
            assert current.lifecycle_state.value == "active"

    def test_failure_on_middle_op_unchanged_state(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(ids[0].id, versions[0].version_id, TransitionType.UPDATE, "ok1"),
            EvolutionOperation(ids[1].id, wrong_vid, TransitionType.UPDATE, "fail"),
            EvolutionOperation(ids[2].id, versions[2].version_id, TransitionType.UPDATE, "ok3"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except OptimisticConcurrencyError:
            uow.rollback()

        for id_ in ids:
            current = repo.get_latest_version(id_.id)
            assert current.lifecycle_state.value == "active"

    def test_failure_on_last_op_unchanged_state(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        wrong_vid = uuid.uuid4()
        ops = (
            EvolutionOperation(ids[0].id, versions[0].version_id, TransitionType.UPDATE, "ok1"),
            EvolutionOperation(ids[1].id, versions[1].version_id, TransitionType.UPDATE, "ok2"),
            EvolutionOperation(ids[2].id, wrong_vid, TransitionType.UPDATE, "fail"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except OptimisticConcurrencyError:
            uow.rollback()

        for id_ in ids:
            current = repo.get_latest_version(id_.id)
            assert current.lifecycle_state.value == "active"

    def test_all_operations_applied_or_none(self):
        repo = InMemoryKnowledgeRepository()
        ids = [repo.create_identity() for _ in range(3)]
        versions = []
        for i, id_ in enumerate(ids):
            v = _make_version(identity_id=id_.id, version_number=1)
            repo.add_version(v)
            versions.append(v)
        ops = tuple(
            EvolutionOperation(id_.id, v.version_id, TransitionType.UPDATE, f"op{i}")
            for i, (id_, v) in enumerate(zip(ids, versions))
        )
        plan = EvolutionPlan(operations=ops, affected_targets=tuple(id_.id for id_ in ids))

        uow = EvolutionUnitOfWork()
        uow.attach(repo, repo)
        uow.begin()
        try:
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
            uow.commit()
        except Exception:
            uow.rollback()
            pytest.fail("should not fail")

        for id_ in ids:
            current = repo.get_latest_version(id_.id)
            assert current.lifecycle_state.value == "archived"


# ---------------------------------------------------------------------------
# EvolutionRecord persistence
# ---------------------------------------------------------------------------

class TestEvolutionRecordPersistence:
    def test_success_record_persisted(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        executor.execute(plan, _make_context())
        records = repo.get_execution_records()
        assert len(records) == 1
        assert records[0].success is True
        assert isinstance(records[0], EvolutionRecord)

    def test_failure_record_persisted(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        wrong_vid = uuid.uuid4()

        for record in repo.get_execution_records():
            pass
        record_count_before = len(repo.get_execution_records())

        try:
            op = EvolutionOperation(identity.id, wrong_vid, TransitionType.UPDATE, "test")
            plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
            executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
            executor.execute(plan, _make_context())
        except OptimisticConcurrencyError:
            from datetime import datetime, timezone
            failure = ExecutionFailureRecord(
                plan_identity=uuid.uuid4(),
                executed_at=datetime.now(timezone.utc),
                failure_reason="OCC mismatch",
                failed_operation_index=0,
                operations_count=1,
                failure_type="optimistic_concurrency",
            )
            repo.save_execution_record(failure)

        records = repo.get_execution_records()
        assert len(records) == record_count_before + 1
        assert not hasattr(records[-1], "success") or records[-1] is failure

    def test_record_immutable(self):
        repo = InMemoryKnowledgeRepository()
        identity = repo.create_identity()
        v1 = _make_version(identity_id=identity.id, version_number=1)
        repo.add_version(v1)
        op = EvolutionOperation(identity.id, v1.version_id, TransitionType.UPDATE, "test")
        plan = EvolutionPlan(operations=(op,), affected_targets=(identity.id,))
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        executor.execute(plan, _make_context())
        records = repo.get_execution_records()
        with pytest.raises(AttributeError):
            records[0].success = False


# ---------------------------------------------------------------------------
# UseCase owns transaction
# ---------------------------------------------------------------------------

class TestUseCaseOwnsTransaction:
    def test_use_case_does_not_expose_uow(self):
        repo = InMemoryKnowledgeRepository()
        planner = _make_planner()
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        use_case = EvolutionUseCase(
            planner=planner,
            executor=executor,
            knowledge_repository=repo,
            evolution_repository=repo,
        )
        assert not hasattr(use_case, "_unit_of_work")
        assert "UnitOfWork" not in type(use_case).__name__

    def test_executor_does_not_commit(self):
        repo = InMemoryKnowledgeRepository()
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        assert not hasattr(executor, "commit")
        assert not hasattr(executor, "rollback")

    def test_executor_does_not_own_transaction(self):
        repo = InMemoryKnowledgeRepository()
        executor = EvolutionExecutor(knowledge_repository=repo, evolution_repository=repo)
        assert not hasattr(executor, "_unit_of_work")
        assert not hasattr(executor, "_uow")


# ---------------------------------------------------------------------------
# EvolutionEngine.plan() — delegation tests
# ---------------------------------------------------------------------------

class TestEnginePlanDelegation:
    def test_engine_plan_returns_evolution_plan(self):
        engine = EvolutionEngine()
        plan = engine.plan(targets=(), category="inspect", context=_make_context())
        assert isinstance(plan, EvolutionPlan)

    def test_engine_empty_targets_empty_plan(self):
        engine = EvolutionEngine()
        plan = engine.plan(targets=(), category="duplicate", context=_make_context())
        assert plan.operations == ()
        assert plan.affected_targets == ()

    def test_engine_identical_input_identical_plan(self):
        engine = EvolutionEngine()
        a, b = uuid.uuid4(), uuid.uuid4()
        targets = (a, b)
        ctx = _make_context()
        plan1 = engine.plan(targets, "conflict", ctx)
        plan2 = engine.plan(targets, "conflict", ctx)
        assert plan1 == plan2


class TestEnginePlanNoApplicationImport:
    def test_plan_does_not_import_application(self):
        import inspect
        source = inspect.getsource(EvolutionEngine.plan)
        assert "brain.application" not in source

    def test_engine_module_does_not_import_application(self):
        import brain.evolution.evolution as module
        import inspect
        source = inspect.getsource(module)
        assert "brain.application" not in source


# ---------------------------------------------------------------------------
# Boundary Isolation
# ---------------------------------------------------------------------------

class TestBoundaryIsolation:
    def test_executor_imports_allowed(self):
        import brain.evolution.executor as mod
        import inspect
        source = inspect.getsource(mod)
        assert "brain.evolution.evolution_context" in source
        assert "brain.evolution.evolution_operation" in source
        assert "brain.evolution.evolution_plan" in source
        assert "brain.evolution.evolution_record" in source
        assert "brain.evolution.transition" in source
        assert "brain.repositories.base" in source
        assert "brain.repositories.evolution_base" in source

    def test_executor_forbidden_imports(self):
        import inspect
        from brain.evolution.executor import EvolutionExecutor
        source = inspect.getsource(EvolutionExecutor)
        assert "brain.application.workflow" not in source
        assert "brain.reflection" not in source
        assert "brain.learning" not in source
        assert "brain.planning" not in source
        assert "brain.runtime" not in source

    def test_planner_no_repository_imports(self):
        import inspect
        from brain.evolution.planning import EvolutionPlanner
        source = inspect.getsource(EvolutionPlanner)
        assert "Repository" not in source

    def test_use_case_imports_planner_and_executor(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "EvolutionPlanner" in source
        assert "EvolutionExecutor" in source
        assert "EvolutionRequest" in source
        assert "EvolutionSummary" in source

    def test_no_repository_import_in_use_case_source(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "from brain.repositories" not in source

    def test_no_runtime_import_in_use_case(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "BrainRuntime" not in source

    def test_no_workflow_import_in_use_case(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Workflow" not in source

    def test_no_reflection_import_in_use_case(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Reflection" not in source

    def test_no_learning_import_in_use_case(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "from brain.learning" not in source


# ---------------------------------------------------------------------------
# EvolutionRequest DTO
# ---------------------------------------------------------------------------

class TestEvolutionRequestDTO:
    def test_creation(self):
        req = _make_request()
        assert isinstance(req, EvolutionRequest)
        assert req.targets == ()
        assert req.context == ""

    def test_with_targets(self):
        t1, t2 = uuid.uuid4(), uuid.uuid4()
        req = _make_request(targets=(t1, t2), context="inspect")
        assert req.targets == (t1, t2)
        assert req.context == "inspect"

    def test_frozen(self):
        req = _make_request()
        with pytest.raises(AttributeError):
            req.targets = ()

    def test_equality(self):
        t1 = uuid.uuid4()
        r1 = EvolutionRequest(targets=(t1,), context="test")
        r2 = EvolutionRequest(targets=(t1,), context="test")
        assert r1 == r2


# ---------------------------------------------------------------------------
# PlanningMetrics DTO
# ---------------------------------------------------------------------------

class TestPlanningMetricsDTO:
    def test_creation(self):
        metrics = PlanningMetrics()
        assert metrics.planned_operations_count == 0
        assert metrics.affected_targets_count == 0
        assert metrics.quarantined_skipped == 0

    def test_with_values(self):
        metrics = PlanningMetrics(planned_operations_count=5, affected_targets_count=3, quarantined_skipped=2)
        assert metrics.planned_operations_count == 5

    def test_frozen(self):
        metrics = PlanningMetrics()
        with pytest.raises(AttributeError):
            metrics.planned_operations_count = 0


# ---------------------------------------------------------------------------
# ExecutionMetrics DTO
# ---------------------------------------------------------------------------

class TestExecutionMetricsDTO:
    def test_creation(self):
        metrics = ExecutionMetrics()
        assert metrics.executed_operations == 0
        assert metrics.successful_operations == 0
        assert metrics.failed_operations == 0
        assert metrics.rolled_back is False
        assert metrics.optimistic_conflicts == 0

    def test_with_values(self):
        from datetime import timedelta
        metrics = ExecutionMetrics(
            executed_operations=5,
            successful_operations=3,
            failed_operations=2,
            rolled_back=True,
            optimistic_conflicts=1,
            transaction_duration=timedelta(seconds=2),
        )
        assert metrics.executed_operations == 5
        assert metrics.successful_operations == 3
        assert metrics.failed_operations == 2
        assert metrics.rolled_back is True
        assert metrics.optimistic_conflicts == 1
        assert metrics.transaction_duration.total_seconds() == 2

    def test_frozen(self):
        metrics = ExecutionMetrics()
        with pytest.raises(AttributeError):
            metrics.executed_operations = 1

    def test_coexists_with_planning_in_summary(self):
        from datetime import timedelta
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=timedelta(seconds=1),
            planning=PlanningMetrics(planned_operations_count=2),
            execution=ExecutionMetrics(executed_operations=2, successful_operations=2),
        )
        assert summary.planning.planned_operations_count == 2
        assert summary.execution.executed_operations == 2
        assert summary.execution.successful_operations == 2


# ---------------------------------------------------------------------------
# EvolutionSummary DTO
# ---------------------------------------------------------------------------

class TestEvolutionSummaryDTO:
    def test_creation(self):
        from datetime import timedelta
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=timedelta(seconds=1),
        )
        assert summary.evolution_started is True
        assert isinstance(summary.planning, PlanningMetrics)
        assert isinstance(summary.execution, ExecutionMetrics)

    def test_frozen(self):
        from datetime import timedelta
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=timedelta(0),
        )
        with pytest.raises(AttributeError):
            summary.evolution_started = False
