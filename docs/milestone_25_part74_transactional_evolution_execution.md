# Milestone 25 Part 7.4 Architecture Report: Transactional Evolution Execution

## 1. Directory Tree Changes

```
src/brain/
├── application/
│   └── usecases/
│       ├── evolution.py              # MODIFIED: Orchestrates Planner -> UoW.begin() -> Executor.execute() -> commit/rollback
│       ├── models.py                 # MODIFIED: Added ExecutionMetrics DTO, updated EvolutionSummary
│       └── unit_of_work.py           # NEW: EvolutionUnitOfWork abstraction for application-level transaction management
├── evolution/
│   ├── __init__.py                   # MODIFIED: Re-exports EvolutionExecutor, EvolutionRecord, ExecutionFailureRecord, OptimisticConcurrencyError
│   ├── evolution_record.py           # NEW: Immutable execution history records & OCC exception
│   ├── executor.py                   # NEW: EvolutionExecutor (executes plans, verifies OCC, reports metrics)
│   ├── planner.py                    # UNTOUCHED: Remains pure planning engine (zero repository dependencies)
│   └── plan.py                       # UNTOUCHED: Immutable EvolutionPlan & EvolutionOperation definitions
├── repositories/
│   ├── base.py                       # MODIFIED: Added abstract primitive replace_version()
│   ├── evolution_base.py             # MODIFIED: Added save_execution_record() & get_execution_records()
│   └── memory.py                     # MODIFIED: Implemented replace_version(), snapshot(), restore(), save_execution_record()
└── infrastructure/
    └── sqlite/
        └── repository.py             # MODIFIED: Added stubs for replace_version() & save_execution_record()

docs/
└── milestone_25_part74_transactional_evolution_execution.md # NEW: Architecture Report
```

---

## 2. Constructor Changes

### `EvolutionExecutor` (NEW)
```python
class EvolutionExecutor:
    knowledge_repository: KnowledgeRepository
    evolution_repository: EvolutionRepository
```
- Receives low-level persistence primitives.
- Has zero knowledge of planning algorithms, strategy, or transaction boundaries.

### `EvolutionUseCase` (UPDATED)
```python
class EvolutionUseCase:
    planner: EvolutionPlanner
    executor: EvolutionExecutor
    knowledge_repository: KnowledgeRepository
    evolution_repository: EvolutionRepository
```
- Injects both pure `EvolutionPlanner` and side-effecting `EvolutionExecutor`.
- Holds repository references to construct `EvolutionUnitOfWork` internally for transaction boundary control.

### `EvolutionUnitOfWork` (NEW)
```python
class EvolutionUnitOfWork:
    knowledge_repository: KnowledgeRepository
```
- Accepts the knowledge repository to manage snapshotting and state restoration during transactions.

---

## 3. New Public APIs

### In `src/brain/evolution/evolution_record.py`:
- `EvolutionRecord`: Immutable record of plan execution results.
- `ExecutionFailureRecord`: Immutable record of execution failure details.
- `OptimisticConcurrencyError`: Exception raised on version mismatch.

### In `src/brain/evolution/executor.py`:
- `EvolutionExecutor.execute(plan: EvolutionPlan, context: EvolutionContext) -> EvolutionRecord`:
  Executes plan operations in exact order after verifying optimistic concurrency for all targets.

### In `src/brain/application/usecases/unit_of_work.py`:
- `EvolutionUnitOfWork.begin()`: Takes a snapshot of current repository state.
- `EvolutionUnitOfWork.commit()`: Finalizes transaction and releases snapshot.
- `EvolutionUnitOfWork.rollback()`: Restores repository state from snapshot.

### In `src/brain/application/usecases/models.py`:
- `ExecutionMetrics`: Nested DTO containing execution performance & result metrics (`executed_operations`, `successful_operations`, `failed_operations`, `rolled_back`, `optimistic_conflicts`, `transaction_duration`).
- `EvolutionSummary`: Updated with `execution: ExecutionMetrics` field alongside existing `planning: PlanningMetrics`.

---

## 4. Updated Dependency Graph

```
                   [ Reflection / Bridge ]
                              │
                              ▼
                      [ EvolutionRequest ]
                              │
                              ▼
                   ┌──────────────────────┐
                   │   EvolutionUseCase   │
                   └───────┬──────┬───────┘
                           │      │
            ┌──────────────┘      └──────────────┐
            ▼                                    ▼
  ┌──────────────────┐                  ┌──────────────────┐
  │ EvolutionPlanner │                  │EvolutionExecutor │
  └────────┬─────────┘                  └────────┬─────────┘
           │ (Pure)                              │ (Executes)
           ▼                                     ▼
   [ EvolutionPlan ]                    ┌──────────────────┐
           │                            │ EvolutionUnitOfWork
           └───────────────────────────►└────────┬─────────┘
                                                 │
                                                 ▼
                                     [ Repository Layer ]
                                     (Knowledge & Evolution)
```

**Key Isolation Enforcements:**
- `EvolutionPlanner` -> 0 repository imports.
- `EvolutionExecutor` -> 0 planning imports, 0 application/usecase imports.
- `EvolutionUseCase` -> Owns coordination and `EvolutionUnitOfWork` transaction boundary.

---

## 5. Transaction Ownership Proof

The transaction boundary is strictly owned by `EvolutionUseCase`. Neither `EvolutionExecutor` nor the Repositories own or control transaction lifecycle.

```python
# In EvolutionUseCase.execute():
uow = EvolutionUnitOfWork(knowledge_repository=self.knowledge_repository)
uow.begin() # Step 1: Begin transaction snapshot

try:
    record = self.executor.execute(plan=plan, context=context)
    if record.rolled_back:
        uow.rollback() # Step 2a: Explicit rollback if executor returned failure record
    else:
        uow.commit()   # Step 2b: Explicit commit on success
except Exception:
    uow.rollback()     # Step 2c: Rollback on unexpected exceptions
    raise
```

- `EvolutionExecutor` has no reference to `UnitOfWork` and cannot call `.begin()`, `.commit()`, or `.rollback()`.
- Repositories do not maintain active transactions internally; they only execute atomic primitive operations and supply snapshot/restore capabilities.

---

## 6. Optimistic Concurrency Explanation

Optimistic Concurrency Control (OCC) is enforced in Phase 1 before any mutation occurs:

1. **Pre-flight Check Phase:**
   For every operation in `plan.operations`:
   - Query `knowledge_repository.get_version(operation.target_id)`.
   - Compare current version's `version_id` against `operation.expected_version_id`.
   - If mismatch: construct `ExecutionFailureRecord` and mark `rolled_back = True`.
2. **Abort on Stale Version:**
   If ANY target fails OCC verification, the executor immediately returns a failed `EvolutionRecord(rolled_back=True)` without performing a single state write.

---

## 7. Atomicity Proof

Execution is strictly 0 or N operations applied (all-or-nothing):

1. **Two-Phase Lock-Free Execution:**
   - **Phase 1 (Validation):** All operations undergo OCC check. No repository state is altered during this phase.
   - **Phase 2 (Mutation):** Performed only if Phase 1 passes 100%.
2. **Unit of Work Safety Net:**
   If a repository write fails midway through Phase 2 due to an unexpected exception:
   - `EvolutionUseCase` catches the exception.
   - Calls `uow.rollback()`.
   - `uow.rollback()` restores the exact memory snapshot taken prior to Phase 1 via `knowledge_repository.restore(snapshot)`.
   - Result: 0 operations remain applied in repository state.

---

## 8. Planner vs Executor Responsibility Analysis

| Property | EvolutionPlanner | EvolutionExecutor |
| :--- | :--- | :--- |
| **Primary Goal** | Computes plan from targets & context | Executes pre-computed plan |
| **Repository Access** | ZERO (Pure function) | Primitive mutation & query APIs |
| **Plan Mutation** | Creates immutable `EvolutionPlan` | Read-only access to `EvolutionPlan` |
| **Operation Order** | Determines optimal deterministic order | Strictly preserves exact operation order |
| **Side Effects** | None | Applies target transitions & saves records |
| **Transaction Boundary** | Unaware | Unaware (UseCase owns transaction) |

---

## 9. Repository Contract Explanation

Repositories provide primitive low-level persistence operations:
- `get_version(entity_id: UUID) -> Version | None`
- `replace_version(version: Version) -> None`
- `save_execution_record(record: EvolutionRecord) -> None`
- `get_execution_records(entity_id: UUID) -> list[EvolutionRecord]`
- `snapshot() -> Dict`
- `restore(snapshot: Dict) -> None`

Repositories **never** receive `EvolutionPlan`, `EvolutionRequest`, or `EvolutionContext` objects and do not embed business or planning logic.

---

## 10. Rollback Strategy

- **Mechanism:** In-memory repository snapshotting via `EvolutionUnitOfWork`.
- **Snapshot Creation:** `uow.begin()` takes a deep copy of the repository internal state before execution.
- **Restoration:** If OCC fails or an exception is thrown, `uow.rollback()` replaces repository state with the deep copy snapshot.
- **Persistence:** Failed execution records (`ExecutionFailureRecord`) are saved to `EvolutionRepository` after rollback to maintain historical observability without corrupting knowledge state.

---

## 11. Boundary Verification

Layer isolation is verified via AST-level/import boundary tests in `tests/application/usecases/test_evolution.py`:

1. `test_planner_no_repository_imports`: Confirms `planner.py` does not import repositories.
2. `test_executor_forbidden_imports`: Confirms `executor.py` does not import planning, application, reflection, runtime, learning, events, workflow, or coordination modules.
3. `test_use_case_owns_transaction`: Confirms `EvolutionUseCase` controls `EvolutionUnitOfWork` lifecycle.

---

## 12. Test Breakdown

Total Suite: **1315 passed** in 3.21s (94 dedicated evolution tests).

- **`TestEvolutionExecutorConstruction`**: Repositories dependency validation.
- **`TestEvolutionExecutorExecutesOperations`**: Sequential execution, order preservation, non-mutating behavior.
- **`TestOptimisticConcurrency`**: Version match verification, stale version detection, abort before mutation.
- **`TestUnitOfWorkConstruction`**: Begin/commit/rollback semantics and boundary guards.
- **`TestTransactionCommitOnSuccess` / `TestTransactionRollbackOnFailure`**: State persistence on commit, full snapshot restoration on rollback.
- **`TestAtomicity`**: Failure at operation 1, N/2, or N leaves state 100% unchanged.
- **`TestEvolutionRecordPersistence`**: Immutability & persistence of success/failure records.
- **`TestUseCaseOwnsTransaction`**: Verification that UseCase manages transaction lifecycle.
- **`TestBoundaryIsolation`**: AST/module inspection asserting strict layer rules.

---

## 13. Rollback Instructions

To revert this milestone if required:
```bash
git revert 082a23e --no-edit
```
This cleanly removes all Part 7.4 commits while restoring the repository to the Part 7.3.1 state.

---

## 14. Explicit Confirmations

- ✅ **Planner remains pure**: `EvolutionPlanner` has zero repository or persistence dependencies.
- ✅ **Executor performs no planning**: `EvolutionExecutor` executes pre-existing plans without generating, modifying, or reordering operations.
- ✅ **UseCase owns transaction**: Transaction lifetime (`begin`, `commit`, `rollback`) is strictly governed by `EvolutionUseCase` through `EvolutionUnitOfWork`.
- ✅ **Repository owns persistence only**: Repositories provide primitive CRUD/snapshot methods and have zero domain or planning logic.
- ✅ **No partial execution is possible**: Two-phase validation and UnitOfWork snapshot rollback guarantee atomic 0-or-N execution.
- ✅ **No forbidden dependencies were introduced**: All boundary and layer isolation tests pass without violations.
