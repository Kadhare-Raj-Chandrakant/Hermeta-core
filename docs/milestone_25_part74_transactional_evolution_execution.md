# Milestone 25 Part 7.4: Transactional Evolution Execution

## Objective
Implement safe, atomic execution of immutable EvolutionPlans with optimistic concurrency, rollback, and execution records — while keeping EvolutionPlanner pure (zero repository dependencies).

## Architecture Rules
- **Planner thinks, Executor acts, UseCase coordinates, Repositories persist**
- EvolutionPlanner must remain pure (no repository imports, no persistence awareness)
- EvolutionExecutor must never plan or reorder operations
- UseCase exclusively owns the transaction boundary (UnitOfWork lifecycle)
- All operations verified (OCC checks) before ANY writes — atomic all-or-nothing
- Rollback restores full prior state via snapshot/restore on knowledge repository

## New Files

### `src/brain/evolution/evolution_record.py`
- `EvolutionRecord` — frozen dataclass: `plan_id`, `plan_hash`, `executed_at`, `operations_attempted`, `operations_succeeded`, `operations_failed`, `rolled_back`, `failure_records`, `transaction_duration`
- `ExecutionFailureRecord` — frozen dataclass: `operation_index`, `failure_type` (str), `target_id`, `details`
- `OptimisticConcurrencyError` — exception with `operation_index`, `target_id`, `expected_version_id`, `actual_version_id`

### `src/brain/evolution/executor.py`
- `EvolutionExecutor(knowledge_repository, evolution_repository)` — frozen dataclass
- `execute(plan, context) -> EvolutionRecord`:
  1. Phase 1 — Verify all OCC: for each operation, check `knowledge_repository.get_version(operation.target_id) == operation.expected_version_id`; collect failures
  2. If OCC failures: abort, return failure record, NO mutations applied
  3. Phase 2 — Apply all operations: for each operation, `knowledge_repository.apply_version(operation.target_id, operation.transition_type, operation.data)` and `evolution_repository.save_transition(...)`
  4. Return success record with timing
- Forbidden imports: planning, application use cases, reflection, runtime, learning, events, session, workflow, coordination

### `src/brain/application/usecases/unit_of_work.py`
- `EvolutionUnitOfWork(knowledge_repository)` — frozen dataclass
- `attach(knowledge_repository)` — attach repo (called in UseCase)
- `begin()` — take snapshot: `knowledge_repository.snapshot()`
- `commit()` — verify state began, clear snapshot
- `rollback()` — restore snapshot: `knowledge_repository.restore(snapshot)`
- Guards: `commit()`/`rollback()` without `begin()` raises `RuntimeError`; double `begin()` raises `RuntimeError`

### `tests/application/usecases/test_evolution.py` (94 tests)
14 test classes covering:
- EvolutionOperation construction, immutability, equality
- EvolutionPlan construction, expected versions
- EvolutionContext construction
- EvolutionRecord / ExecutionFailureRecord / OptimisticConcurrencyError
- EvolutionUseCase construction (frozen)
- UseCase execute: planning-only flow (5 tests), execution metrics (3 tests)
- EvolutionPlanner plan logic (7 tests)
- EvolutionExecutor construction & execution (5 tests)
- Optimistic concurrency (4 tests)
- UnitOfWork lifecycle (6 tests)
- Transaction commit on success (1 test)
- Transaction rollback on failure (3 tests)
- Atomicity (4 tests)
- EvolutionRecord persistence (3 tests)
- UseCase owns transaction boundary (3 tests)
- Engine plan delegation (3 tests)
- Boundary isolation (9 tests)
- DTO tests: EvolutionRequest, PlanningMetrics, ExecutionMetrics, EvolutionSummary

## Modified Files

### `src/brain/repositories/base.py`
Added abstract method `replace_version(version: Version) -> None`

### `src/brain/repositories/evolution_base.py`
Added abstract methods: `save_execution_record(record: EvolutionRecord) -> None`, `get_execution_records(entity_id: UUID) -> list[EvolutionRecord]`

### `src/brain/repositories/memory.py`
Added:
- `snapshot()` — returns deep copy of `_knowledge`
- `restore(snapshot)` — restores `_knowledge` from snapshot
- `replace_version(version)` — replaces version in store
- `save_execution_record(record)` — stores record
- `get_execution_records(entity_id)` — returns records for entity

### `src/brain/infrastructure/sqlite/repository.py`
Added stub implementations:
- `replace_version(version)` — `pass` (placeholder)
- `save_execution_record(record)` — `pass` (placeholder)
- `get_execution_records(entity_id)` — returns `[]`

### `src/brain/application/usecases/models.py`
Added `ExecutionMetrics` frozen dataclass:
- `executed_operations: int`
- `successful_operations: int`
- `failed_operations: int`
- `rolled_back: bool`
- `optimistic_conflicts: int`
- `transaction_duration: float`
Updated `EvolutionSummary` to include `execution: ExecutionMetrics` (default `ExecutionMetrics(0,0,0,False,0,0.0)`)

### `src/brain/application/usecases/evolution.py`
Rewritten `EvolutionUseCase`:
- Constructor: `EvolutionUseCase(planner: EvolutionPlanner, executor: EvolutionExecutor, knowledge_repository: KnowledgeRepository, evolution_repository: EvolutionRepository)` — frozen
- `execute(request, context)`:
  1. Plan: `planner.plan(request.targets, request.context, context)` — may raise (planning failure)
  2. Begin UoW: `uow.begin()`
  3. Execute: `executor.execute(plan, context)`:
     - On success → `uow.commit()`, return success summary
     - On OCC error → `uow.rollback()`, return failure summary with execution metrics
     - On other exception → `uow.rollback()`, re-raise
  4. Build `EvolutionSummary` with both `planning` and `execution` metrics

### `src/brain/evolution/__init__.py`
Exports: `EvolutionRecord`, `ExecutionFailureRecord`, `EvolutionExecutor`, `OptimisticConcurrencyError`

## Layer Isolation
- `EvolutionPlanner` imports: `EvolutionPlan`, `EvolutionOperation`, `EvolutionContext`, `TransitionType`, `uuid`, `dataclasses` — NO repository imports
- `EvolutionExecutor` imports: `EvolutionRecord`, `ExecutionFailureRecord`, `OptimisticConcurrencyError`, `EvolutionPlan`, `EvolutionOperation`, `EvolutionContext`, `EvolutionRepository`, `KnowledgeRepository`, `TransitionType`, `uuid`, `dataclasses`, `time` — NO planning, application use cases, reflection, runtime, learning, events, session, workflow, coordination imports
- `EvolutionUseCase` imports: `EvolutionPlanner`, `EvolutionExecutor`, `EvolutionUnitOfWork`, `EvolutionRequest`, `EvolutionSummary`, `PlanningMetrics`, `ExecutionMetrics`, `EvolutionPlan`, `EvolutionContext` — NO direct repository imports, NO runtime/workflow/reflection/learning imports
- 9 boundary isolation tests enforce these rules

## Test Coverage Summary
- 1315 total tests (all passing)
- 94 evolution use case tests
- All existing tests pass with no regressions

## Key Design Decisions
1. **Two-phase execution**: OCC verification (read-only) before mutation (write) ensures atomicity
2. **Snapshot/restore on knowledge repo**: Simplest correct rollback — full state capture before mutation
3. **UoW as separate component**: UseCase exclusively owns begin/commit/rollback; executor never touches transaction boundary
4. **ExecutionMetrics as separate DTO**: PlanningMetrics and ExecutionMetrics coexist as independent fields in EvolutionSummary, not merged
5. **Stubs for SQLite**: `replace_version()`/`save_execution_record()` are `pass`/`[]` stubs — full SQLite integration deferred to later milestone
