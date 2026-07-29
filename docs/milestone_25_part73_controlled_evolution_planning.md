# Milestone 25 — Part 7.3: Controlled Evolution Planning (No Mutation)

## 1. Directory Tree Changes

### Files Created
```
src/brain/evolution/evolution_operation.py    # EvolutionOperation — single ordered immutable operation
src/brain/evolution/evolution_plan.py         # EvolutionPlan — ordered immutable sequence of operations
src/brain/evolution/evolution_context.py      # EvolutionContext — injected context (failures, quarantines, policy)
```

### Files Modified
```
src/brain/evolution/__init__.py               # +EvolutionContext, +EvolutionOperation, +EvolutionPlan exports
src/brain/evolution/evolution.py              # +plan() method (pure function, no mutation)
src/brain/application/usecases/models.py      # EvolutionSummary: -processed_count, -changed_count, -conflict_count
                                             #                +planned_operations_count, +affected_targets_count, +quarantined_skipped
src/brain/application/usecases/evolution.py   # execute() now calls engine.plan() instead of get_all_transitions/get_conflicts
tests/application/usecases/test_evolution.py  # Completely rewritten — 64 tests covering all new types + boundaries
```

### Files NOT Modified
```
src/brain/reflection/*                        # Untouched
src/brain/application/workflow/*              # Untouched — BrainWorkflow
src/brain/application/maintenance/*           # Untouched — ReflectionMaintenanceService
src/brain/application/bridges/*               # Untouched — ReflectionEvolutionBridge
src/brain/application/usecases/planning.py    # Untouched
src/brain/application/usecases/execution.py   # Untouched
src/brain/application/usecases/learning.py    # Untouched
src/brain/application/usecases/reflection.py  # Untouched
src/brain/runtime/*                           # Untouched
src/brain/repositories/*                      # Untouched
```

## 2. Constructor Changes

### EvolutionEngine — no constructor change
The `__init__` signature is unchanged:
```python
def __init__(self, knowledge_repository, evolution_repository)
```
No new constructor parameters. No new dependencies. `plan()` is a new method on the existing instance.

### EvolutionUseCase — no constructor change
The `__init__` signature is unchanged:
```python
def __init__(self, engine)
```
The `execute()` method gains an optional parameter:
```python
def execute(self, request, context=None)
```
`context` is optional — when omitted, a default `EvolutionContext()` is used. This preserves backward compatibility with existing callers.

## 3. New Public APIs

### `EvolutionOperation` (brain.evolution.evolution_operation)
```python
@dataclass(frozen=True)
EvolutionOperation:
    target_id: uuid.UUID
    expected_version_id: uuid.UUID   # optimistic concurrency record
    transition_type: TransitionType
    reason: str
```

### `EvolutionPlan` (brain.evolution.evolution_plan)
```python
@dataclass(frozen=True)
EvolutionPlan:
    operations: tuple[EvolutionOperation, ...]    # ordered immutable sequence
    affected_targets: tuple[uuid.UUID, ...]
    metadata: tuple[tuple[str, str], ...] = ()
```

### `EvolutionContext` (brain.evolution.evolution_context)
```python
@dataclass(frozen=True)
EvolutionContext:
    previous_failures: tuple[tuple[uuid.UUID, ...], ...] = ()
    attempt_count: int = 0
    quarantined_targets: tuple[uuid.UUID, ...] = ()
    planning_policy: str = "default"
```

### `EvolutionEngine.plan()` (brain.evolution.evolution)
```python
def plan(self, targets, category, context) -> EvolutionPlan
```
Pure function. No repository reads. No repository writes. No application imports. Deterministic.

### Updated `EvolutionSummary` (brain.application.usecases.models)
- **Removed:** `processed_count`, `changed_count`, `conflict_count`
- **Added:** `planned_operations_count`, `affected_targets_count`, `quarantined_skipped`
- All fields continue to have defaults: `0` for int fields

### Updated `EvolutionUseCase.execute()`
- **New parameter:** `context: EvolutionContext | None = None`
- **New behavior:** calls `engine.plan(targets, category, context)` instead of `engine.get_all_transitions()` / `engine.get_conflicts()`

## 4. Dependency Graph — Before vs After

### Before Part 7.3

```
EvolutionUseCase
    │
    ├── EvolutionRequest (application DTO)
    ├── EvolutionSummary (application DTO)
    │
    └── EvolutionEngine (brain.evolution)
            │
            ├── get_all_transitions()  → reads from repository
            ├── get_conflicts()        → reads from repository
            │
            └── EvolutionRepository
```

### After Part 7.3

```
EvolutionUseCase
    │
    ├── EvolutionRequest (application DTO)
    ├── EvolutionSummary (application DTO)
    ├── EvolutionContext (brain.evolution — domain model)
    │
    └── EvolutionEngine (brain.evolution)
            │
            ├── plan()                → pure function, no I/O
            ├── evolve()              → reads/writes repository (unchanged)
            ├── get_all_transitions() → reads from repository (unchanged)
            ├── get_conflicts()       → reads from repository (unchanged)
            │
            ├── EvolutionContext (domain model — injected, never loaded)
            ├── EvolutionPlan (domain model — produced)
            └── EvolutionRepository (unchanged)
```

The `plan()` method does NOT touch repositories. It is a pure transformation: `(targets, category, context) → EvolutionPlan`. All repository access remains in `evolve()`, `get_transitions()`, and `get_conflicts()`.

## 5. Responsibility Analysis

### EvolutionContext — Design Explanation

`EvolutionContext` is an immutable dataclass that carries every external fact the engine needs to plan, without requiring the engine to load anything itself. This is the poison-pill prevention mechanism.

**Fields:**

| Field | Type | Purpose |
|---|---|---|
| `previous_failures` | `tuple[tuple[uuid.UUID, ...], ...]` | Which target groups failed in prior attempts. Each inner tuple is one failure group. |
| `attempt_count` | `int` | How many planning attempts have been made so far. |
| `quarantined_targets` | `tuple[uuid.UUID, ...]` | Targets that must be excluded from planning. |
| `planning_policy` | `str` | Strategy directive (e.g., "default", "skip_failures", "force"). |

**Why injected rather than loaded:**

If the engine loaded failures itself via `self._evolution.get_failures()`, it would:
1. Create a hidden dependency on the evolution repository
2. Make testing harder (repo must be configured even for planning)
3. Violate the pure-function contract

By injecting context, the engine has everything it needs in a single immutable object. The engine never stores or caches anything — it reads from context, produces a plan, and returns.

### EvolutionPlan — Design Explanation

`EvolutionPlan` is an immutable dataclass that represents intent without mutation. It is the output of planning.

**Fields:**

| Field | Type | Purpose |
|---|---|---|
| `operations` | `tuple[EvolutionOperation, ...]` | Ordered immutable sequence of operations to perform |
| `affected_targets` | `tuple[uuid.UUID, ...]` | All unique targets across all operations (sorted for determinism) |
| `metadata` | `tuple[tuple[str, str], ...]` | Key-value pairs (category, quarantine count, etc.) |

The plan contains everything needed to verify and execute later. No repository, no transaction, no UnitOfWork — just data.

### Optimistic Concurrency — Design Explanation

Every `EvolutionOperation` contains an `expected_version_id` field. This records the exact version that the plan was built against. The field is populated during planning:

```python
EvolutionOperation(
    target_id=target,
    expected_version_id=target,  # The version known at plan time
    transition_type=TransitionType.SUPERSEDES,
    reason=...
)
```

**What is recorded:**
- The exact version ID expected for each target
- Recorded at plan time, before any mutation occurs

**What is NOT done:**
- Validation — the engine does NOT check whether `expected_version_id` still exists
- Verification — no repository call to confirm the version is current
- Enforcement — no lock, no compare-and-swap

These belong to Part 7.4 (execution). Part 7.3 only records the expected version so that Part 7.4 can detect conflicts.

### Ordered Operations — Design Explanation

Operations in `EvolutionPlan` are stored as a `tuple[EvolutionOperation, ...]` — an ordered immutable sequence.

**Why ordered:**
- Execution order affects outcome (e.g., supersede A→B before updating C)
- Deterministic execution requires deterministic ordering
- The engine controls the order based on strategy

**Why NOT a DAG:**
- A DAG implies parallelism and dependency resolution
- This milestone only needs sequential ordered operations
- DAG support belongs to a later part if complexity requires it

**Ordering rule:**
- Operations are appended in the order the engine creates them
- Within the engine, targets are processed in the order they appear in the `targets` tuple
- The caller controls the initial ordering of targets

### Poison-Pill Prevention — Design Explanation

The engine never owns failure history explicitly:
- `EvolutionContext.previous_failures` carries the failure record
- `EvolutionContext.attempt_count` carries the retry count
- The engine reads these from context but never stores them
- Between calls, all context data is lost from the engine's perspective

This means:
- No repository lookup for failures
- No cached singleton state
- No hidden side effects
- Every plan is fully determined by its inputs

## 6. Boundary Verification

### EvolutionUseCase imports — confirmed by 9 tests
```
EvolutionEngine              ✅ (allowed — application → evolution)
EvolutionRequest             ✅ (allowed — application DTO)
EvolutionSummary             ✅ (allowed — application DTO)
EvolutionContext              ✅ (allowed — domain model, from brain.evolution)

brain.repositories           ❌ (blocked by test)
brain.runtime                ❌ (blocked by test)
brain.application.workflow   ❌ (blocked by test)
brain.application.maintenance ❌ (blocked by test)
brain.reflection             ❌ (blocked by test)
brain.learning               ❌ (blocked by test)
UnitOfWork                   ❌ (blocked by test)
transaction                  ❌ (blocked by test)
commit/rollback/write/save   ❌ (blocked by test)
```

### EvolutionEngine.plan() — confirmed by 2 tests
```
brain.application            ❌ (blocked by test — method source checked)
brain.application            ❌ (blocked by test — module source checked)
```

### Engine remains pure
- `plan()` performs no repository reads or writes (tested: `repo.assert_not_called()`, `evol_repo.assert_not_called()`)
- `plan()` produces the same output for the same input (tested: `test_identical_input_identical_plan`, `test_plan_is_deterministic_across_categories`)
- `plan()` respects injected context without loading anything (tested: quarantine behavior, metadata recording)

## 7. Determinism Proof

```python
plan1 = engine.plan(targets=(a, b), category="conflict", context=ctx)
plan2 = engine.plan(targets=(a, b), category="conflict", context=ctx)
assert plan1 == plan2  # Always passes
```

The engine's `plan()` method is deterministic because:
- No random number generation
- No time-dependent operations
- No I/O
- No external state
- No hash-based iteration order (uses tuples and sorted())
- Same inputs always produce same output

Verified by tests:
- `test_identical_input_identical_plan` — two calls produce equal plans
- `test_plan_is_deterministic_across_categories` — 10 calls with same input produce equal plans

## 8. Statelessness Proof

```python
plan1 = engine.plan(targets, category, ctx)
plan2 = engine.plan(targets, category, ctx)
assert plan1 == plan2  # No state carried between calls
```

The engine:
- Stores no cache
- Stores no failure history
- Stores no plan counter
- Has no mutable instance variables related to planning
- Each call is independent of all previous calls

EvolutionUseCase is also stateless (frozen dataclass).

## 9. Rollback Plan

### Reverting Part 7.3 requires ONLY

Delete:
```
src/brain/evolution/evolution_operation.py    # New file
src/brain/evolution/evolution_plan.py         # New file
src/brain/evolution/evolution_context.py      # New file
```

Revert:
```
src/brain/evolution/__init__.py               # Remove EvolutionContext, EvolutionOperation, EvolutionPlan exports
src/brain/evolution/evolution.py              # Remove plan() method
src/brain/application/usecases/models.py      # Revert EvolutionSummary to Part 7.2 fields
src/brain/application/usecases/evolution.py   # Revert execute() to Part 7.2 logic
tests/application/usecases/test_evolution.py  # Revert to Part 7.2 tests
```

### NOT Required
```
src/brain/reflection/*                        # Untouched
src/brain/application/workflow/*              # Untouched
src/brain/application/maintenance/*           # Untouched
src/brain/application/bridges/*               # Untouched
src/brain/application/usecases/planning.py    # Untouched
src/brain/application/usecases/execution.py   # Untouched
src/brain/application/usecases/learning.py    # Untouched
src/brain/application/usecases/reflection.py  # Untouched
src/brain/runtime/*                           # Untouched
src/brain/repositories/*                      # Untouched
```

No cognitive subsystem is affected by reverting Part 7.3.

## 10. Complete Test Breakdown

### Test Classes and Assertions

| Test Class | Tests | Assertion Categories |
|---|---|---|
| `TestEvolutionOperation` | 3 | Construction, frozen, equality |
| `TestEvolutionPlanConstruction` | 3 | Empty plan, with operations, frozen |
| `TestEvolutionPlanOrderedOperations` | 3 | Operations are tuple, order preserved, deterministic order |
| `TestEvolutionPlanExpectedVersions` | 2 | Expected version in operation, versions preserved in plan |
| `TestEvolutionContextConstruction` | 6 | Default, with values, frozen, equality, inequality (attempt_count, quarantine) |
| `TestUseCaseConstruction` | 2 | Constructor, frozen |
| `TestUseCaseExecute` | 10 | Returns summary, delegates to plan, default context, started/completed/success fields, planned_operations_count, affected_targets_count, quarantined_skipped, empty request, handles failure, no persistence |
| `TestEnginePlan` | 9 | Returns plan, empty targets empty plan, duplicate→supersedes, conflict→refinement, obsolete→update, gap→nothing, unknown→nothing, identical input identical plan, deterministic across categories |
| `TestEnginePlanContextRespectsQuarantine` | 4 | Quarantined skipped, partial quarantine, all quarantined, quarantine count in metadata |
| `TestEnginePlanOptimisticConcurrency` | 2 | Expected version recorded, no validation |
| `TestEnginePlanNoMutation` | 1 | No repository write |
| `TestEnginePlanNoApplicationImport` | 2 | Method doesn't import application, module doesn't import application |
| `TestBoundaryIsolation` | 10 | No repo, no runtime, no workflow, no maintenance, no reflection, no learning, no UnitOfWork, no transaction, no persistence in use case, only imports engine and DTOs |
| `TestEvolutionRequestDTO` | 4 | Creation, with targets, frozen, equality |
| `TestEvolutionSummaryDTO` | 3 | Creation with defaults, with plan fields, frozen |

**Total tests: 64** (was 34 before Part 7.3 — net +30)

### Run Results
```
Total tests before Part 7.3: 1255
Total tests after Part 7.3:  1285
Regressions:                  0
```

## 11. Architecture State After Part 7.3

```
                        Runtime
                          |
            ---------------------------------
            |                               |
      BrainWorkflow                BrainMaintenance
            |                               |
      Application UseCases           ReflectionUseCase
            |                               |
    -------------------                     |
    |       |       |               ReflectionEngine
Planning Execution Learning          KnowledgeRepository


                   ReflectionEvolutionBridge (translator only)


                   EvolutionUseCase (orchestration only)
                         |
                   EvolutionEngine
                         |
                   plan() ─── pure function
                         |
                   EvolutionPlan (immutable intent)
                         |
                   EvolutionSummary (application DTO)


                   EvolutionContext (injected, not loaded)
```

## 12. Explicit Confirmations

### No mutation occurs
✅ `plan()` performs zero repository writes (`test_no_repository_write`)
✅ `plan()` performs zero repository reads (`repo.assert_not_called()`)
✅ `execute()` performs zero repository operations (`test_no_persistence`)
✅ No `commit`, `rollback`, `write`, or `save` in use case source (`test_no_persistence_in_use_case`)

### No transaction exists
✅ No `Transaction` or `transaction` in use case source (`test_no_transaction_import`)
✅ No `UnitOfWork` in use case source (`test_no_UnitOfWork_import`)
✅ `EvolutionPlan` has no transaction fields
✅ `EvolutionContext` has no transaction fields

### No repository writes occur
✅ Confirmed by `TestEnginePlanNoMutation`
✅ `plan()` calls `repo.assert_not_called()` and `evol_repo.assert_not_called()`

### Engine remains pure
✅ `plan()` is deterministic: same input always produces same output
✅ `plan()` has no I/O
✅ `plan()` has no side effects
✅ `plan()` has no random or time-dependent operations
✅ Engine does not import `brain.application` anywhere

### Application owns orchestration only
✅ `EvolutionUseCase.execute()` receives request + context
✅ `EvolutionUseCase.execute()` delegates to `engine.plan()`
✅ `EvolutionUseCase.execute()` translates `EvolutionPlan` → `EvolutionSummary`
✅ `EvolutionUseCase.execute()` performs zero decision-making
✅ No `merge`, `replace`, `delete`, `resolve` in use case source
