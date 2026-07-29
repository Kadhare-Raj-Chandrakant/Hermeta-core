import uuid

import pytest

from brain.application.usecases.evolution import EvolutionUseCase
from brain.application.usecases.models import EvolutionRequest, EvolutionSummary
from brain.evolution.evolution import EvolutionEngine
from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_operation import EvolutionOperation
from brain.evolution.evolution_plan import EvolutionPlan
from brain.evolution.transition_type import TransitionType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine() -> EvolutionEngine:
    from unittest.mock import MagicMock
    return MagicMock(spec=EvolutionEngine)


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
        plan = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
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


class TestEvolutionPlanOrderedOperations:
    def test_operations_are_tuple(self):
        plan = EvolutionPlan(operations=(), affected_targets=())
        assert isinstance(plan.operations, tuple)

    def test_order_is_preserved(self):
        tid1, tid2, tid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        ops = (
            EvolutionOperation(tid1, tid1, TransitionType.UPDATE, "first"),
            EvolutionOperation(tid2, tid2, TransitionType.SUPERSEDES, "second"),
            EvolutionOperation(tid3, tid3, TransitionType.REFINEMENT, "third"),
        )
        plan = EvolutionPlan(operations=ops, affected_targets=(tid1, tid2, tid3))
        assert plan.operations[0].reason == "first"
        assert plan.operations[1].reason == "second"
        assert plan.operations[2].reason == "third"

    def test_deterministic_order(self):
        tid1, tid2 = uuid.uuid4(), uuid.uuid4()
        ops = (
            EvolutionOperation(tid1, tid1, TransitionType.UPDATE, "a"),
            EvolutionOperation(tid2, tid2, TransitionType.UPDATE, "b"),
        )
        plan1 = EvolutionPlan(operations=ops, affected_targets=(tid1, tid2))
        plan2 = EvolutionPlan(operations=ops, affected_targets=(tid1, tid2))
        assert plan1 == plan2


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
        assert op.expected_version_id != op.target_id  # prove they're separate fields

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
# EvolutionUseCase
# ---------------------------------------------------------------------------

class TestUseCaseConstruction:
    def test_constructor(self):
        engine = _make_engine()
        use_case = EvolutionUseCase(engine=engine)
        assert use_case.engine is engine

    def test_frozen(self):
        engine = _make_engine()
        use_case = EvolutionUseCase(engine=engine)
        with pytest.raises(AttributeError):
            use_case.engine = None


class TestUseCaseExecute:
    def test_returns_evolution_summary(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert isinstance(result, EvolutionSummary)

    def test_delegates_to_engine_plan(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        req = _make_request(targets=(uuid.uuid4(),), context="duplicate")
        ctx = _make_context()
        use_case.execute(req, ctx)
        engine.plan.assert_called_once_with(
            targets=req.targets,
            category=req.context,
            context=ctx,
        )

    def test_uses_default_context_when_none(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        use_case.execute(_make_request())
        call_kwargs = engine.plan.call_args
        assert isinstance(call_kwargs[1]["context"], EvolutionContext)

    def test_summary_started_completed_success(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert result.evolution_started is True
        assert result.evolution_completed is True
        assert result.evolution_success is True

    def test_summary_planned_operations_count(self):
        engine = _make_engine()
        tid = uuid.uuid4()
        ops = (
            EvolutionOperation(tid, tid, TransitionType.UPDATE, "op1"),
            EvolutionOperation(tid, tid, TransitionType.REFINEMENT, "op2"),
        )
        engine.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid,),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert result.planned_operations_count == 2

    def test_summary_affected_targets_count(self):
        engine = _make_engine()
        tid1, tid2 = uuid.uuid4(), uuid.uuid4()
        ops = (
            EvolutionOperation(tid1, tid1, TransitionType.UPDATE, "op1"),
            EvolutionOperation(tid2, tid2, TransitionType.UPDATE, "op2"),
        )
        engine.plan.return_value = EvolutionPlan(
            operations=ops,
            affected_targets=(tid1, tid2),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert result.affected_targets_count == 2

    def test_summary_quarantined_skipped(self):
        engine = _make_engine()
        tid = uuid.uuid4()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
            metadata=(
                ("category", "duplicate"),
                ("quarantined_skipped", "2"),
            ),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert result.quarantined_skipped == 2

    def test_summary_empty_request(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        result = use_case.execute(_make_request(), _make_context())
        assert result.planned_operations_count == 0
        assert result.affected_targets_count == 0

    def test_handles_planning_failure(self):
        engine = _make_engine()
        engine.plan.side_effect = RuntimeError("plan failed")
        use_case = EvolutionUseCase(engine=engine)
        with pytest.raises(RuntimeError, match="plan failed"):
            use_case.execute(_make_request(), _make_context())

    def test_no_persistence(self):
        engine = _make_engine()
        engine.plan.return_value = EvolutionPlan(
            operations=(),
            affected_targets=(),
        )
        use_case = EvolutionUseCase(engine=engine)
        use_case.execute(_make_request(), _make_context())
        assert not hasattr(use_case, "_repository")
        assert not hasattr(use_case, "_unit_of_work")
        assert not hasattr(use_case, "_transaction")


# ---------------------------------------------------------------------------
# EvolutionEngine.plan() — integration tests (real engine with mock repos)
# ---------------------------------------------------------------------------

class TestEnginePlan:
    def test_plan_returns_evolution_plan(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        plan = engine.plan(
            targets=(),
            category="inspect",
            context=_make_context(),
        )
        assert isinstance(plan, EvolutionPlan)

    def test_empty_targets_empty_plan(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        plan = engine.plan(
            targets=(),
            category="duplicate",
            context=_make_context(),
        )
        assert plan.operations == ()
        assert plan.affected_targets == ()

    def test_duplicate_plans_supersedes(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b = uuid.uuid4(), uuid.uuid4()
        plan = engine.plan(
            targets=(a, b),
            category="duplicate",
            context=_make_context(),
        )
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.SUPERSEDES
        assert plan.operations[0].target_id == a
        assert plan.operations[0].expected_version_id == a

    def test_conflict_plans_refinement(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b = uuid.uuid4(), uuid.uuid4()
        plan = engine.plan(
            targets=(a, b),
            category="conflict",
            context=_make_context(),
        )
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.REFINEMENT

    def test_obsolete_plans_update(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a = uuid.uuid4()
        plan = engine.plan(
            targets=(a,),
            category="obsolete",
            context=_make_context(),
        )
        assert len(plan.operations) == 1
        assert plan.operations[0].transition_type == TransitionType.UPDATE

    def test_gap_plans_nothing(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a = uuid.uuid4()
        plan = engine.plan(
            targets=(a,),
            category="gap",
            context=_make_context(),
        )
        assert plan.operations == ()

    def test_unknown_category_plans_nothing(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a = uuid.uuid4()
        plan = engine.plan(
            targets=(a,),
            category="unknown",
            context=_make_context(),
        )
        assert plan.operations == ()

    def test_identical_input_identical_plan(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b = uuid.uuid4(), uuid.uuid4()
        targets = (a, b)
        ctx = _make_context()
        plan1 = engine.plan(targets, "conflict", ctx)
        plan2 = engine.plan(targets, "conflict", ctx)
        assert plan1 == plan2

    def test_plan_is_deterministic_across_categories(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        targets = (uuid.uuid4(), uuid.uuid4())
        ctx = _make_context()
        results = [engine.plan(targets, "duplicate", ctx) for _ in range(10)]
        assert all(r == results[0] for r in results)


class TestEnginePlanContextRespectsQuarantine:
    def test_quarantined_targets_skipped(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b = uuid.uuid4(), uuid.uuid4()
        ctx = _make_context(quarantined_targets=(a,))
        plan = engine.plan(
            targets=(a, b),
            category="duplicate",
            context=ctx,
        )
        assert len(plan.operations) == 0

    def test_partial_quarantine(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b, c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        ctx = _make_context(quarantined_targets=(a,))
        plan = engine.plan(
            targets=(a, b, c),
            category="duplicate",
            context=ctx,
        )
        assert len(plan.operations) == 1
        assert plan.operations[0].target_id == b

    def test_all_targets_quarantined(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b = uuid.uuid4(), uuid.uuid4()
        ctx = _make_context(quarantined_targets=(a, b))
        plan = engine.plan(
            targets=(a, b),
            category="duplicate",
            context=ctx,
        )
        assert plan.operations == ()

    def test_plan_metadata_records_quarantine_count(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a, b, c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        ctx = _make_context(quarantined_targets=(a,))
        plan = engine.plan(
            targets=(a, b, c),
            category="obsolete",
            context=ctx,
        )
        for key, val in plan.metadata:
            if key == "quarantined_skipped":
                assert val == "1"
                break
        else:
            pytest.fail("quarantined_skipped not in metadata")


class TestEnginePlanOptimisticConcurrency:
    def test_expected_version_recorded(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a = uuid.uuid4()
        plan = engine.plan(
            targets=(a,),
            category="obsolete",
            context=_make_context(),
        )
        assert plan.operations[0].expected_version_id == a

    def test_no_validation_of_expected_versions(self):
        from unittest.mock import MagicMock
        engine = EvolutionEngine(
            knowledge_repository=MagicMock(),
            evolution_repository=MagicMock(),
        )
        a = uuid.uuid4()
        # The plan() method does NOT check whether the expected version exists.
        # It just records it.
        plan = engine.plan(
            targets=(a,),
            category="obsolete",
            context=_make_context(),
        )
        assert plan.operations[0].expected_version_id is not None


class TestEnginePlanNoMutation:
    def test_no_repository_write(self):
        from unittest.mock import MagicMock
        repo = MagicMock()
        evol_repo = MagicMock()
        engine = EvolutionEngine(
            knowledge_repository=repo,
            evolution_repository=evol_repo,
        )
        a = uuid.uuid4()
        engine.plan(
            targets=(a,),
            category="duplicate",
            context=_make_context(),
        )
        repo.assert_not_called()
        evol_repo.assert_not_called()


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
        assert "EvolutionUseCase" not in source
        assert "EvolutionRequest" not in source


# ---------------------------------------------------------------------------
# Boundary Isolation
# ---------------------------------------------------------------------------

class TestBoundaryIsolation:
    def test_no_repository_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Repository" not in source
        assert "from brain.repositories" not in source

    def test_no_runtime_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "BrainRuntime" not in source
        assert "from brain.runtime" not in source

    def test_no_workflow_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Workflow" not in source
        assert "from brain.application.workflow" not in source

    def test_no_maintenance_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Maintenance" not in source
        assert "from brain.application.maintenance" not in source

    def test_no_reflection_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Reflection" not in source
        assert "from brain.reflection" not in source

    def test_no_learning_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "from brain.learning" not in source

    def test_no_UnitOfWork_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "UnitOfWork" not in source
        assert "unit_of_work" not in source.lower()

    def test_no_transaction_import(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "Transaction" not in source
        assert "transaction" not in source.lower()

    def test_no_persistence_in_use_case(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "commit" not in source.lower()
        assert "rollback" not in source.lower()
        assert "write" not in source.lower()
        assert "save" not in source.lower()

    def test_use_case_only_imports_engine_and_dtos(self):
        import inspect
        source = inspect.getsource(EvolutionUseCase)
        assert "EvolutionEngine" in source
        assert "EvolutionRequest" in source
        assert "EvolutionSummary" in source
        assert "EvolutionContext" in source


# ---------------------------------------------------------------------------
# EvolutionRequest (existing DTO tests preserved)
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
# EvolutionSummary DTO
# ---------------------------------------------------------------------------

class TestEvolutionSummaryDTO:
    def test_creation(self):
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=__import__("datetime").timedelta(seconds=1),
        )
        assert summary.evolution_started is True
        assert summary.planned_operations_count == 0
        assert summary.affected_targets_count == 0
        assert summary.quarantined_skipped == 0

    def test_with_plan_fields(self):
        from datetime import timedelta
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=timedelta(seconds=1),
            planned_operations_count=5,
            affected_targets_count=3,
            quarantined_skipped=2,
        )
        assert summary.planned_operations_count == 5
        assert summary.affected_targets_count == 3
        assert summary.quarantined_skipped == 2

    def test_frozen(self):
        summary = EvolutionSummary(
            evolution_started=True,
            evolution_completed=True,
            evolution_success=True,
            evolution_duration=__import__("datetime").timedelta(0),
        )
        with pytest.raises(AttributeError):
            summary.planned_operations_count = 0
