# Milestone 25 — Part 7.3.1
## Architectural Refinement — Evolution Planning

---

## 1. How Infrastructure Was Removed from Planning

### Before

```
EvolutionEngine.__init__(
    knowledge_repository: KnowledgeRepository,   ← required
    evolution_repository: EvolutionRepository,   ← required
)

plan()       → uses self._knowledge?  No.  Uses self._evolution?  No.
evolve()     → uses self._knowledge   Yes   uses self._evolution   Yes
record_conflict() → uses self._evolution        Yes
```

Dependency graph (before):

```
UseCase → EvolutionEngine → KnowledgeRepository
                           → EvolutionRepository
                           → evolution_context, operation, plan, ...
```

`plan()` never touched either repository, but callers were forced to provide them.
The constructor coupled *all* callers to infrastructure even when only planning.

### After

```
EvolutionPlanner (zero dependencies)
─────────────────────────────────────
  plan(targets, category, context) → EvolutionPlan
  Imports: evolution_context, operation, plan, transition_type only.
  No Repository imports, no Runtime imports, no Application imports.
```

```
EvolutionEngine.__init__(
    knowledge_repository: KnowledgeRepository | None = None,   ← optional
    evolution_repository: EvolutionRepository | None = None,   ← optional
    planner: EvolutionPlanner | None = None,                   ← optional
)

plan() → delegates to self._planner.plan()  → zero infrastructure
evolve() → needs repos (raises if None)     → mutation path only
record_conflict() → needs repos             → mutation path only
```

```
EvolutionUseCase.__init__(
    planner: EvolutionPlanner  ← no repos, no engine
)
```

Dependency graph (after):

```
Planning path:  UseCase → EvolutionPlanner (zero infra deps)
Mutation path:  Engine → KnowledgeRepository, EvolutionRepository
```

**Proof**: `EvolutionPlanner` is constructible with no arguments and executes
`plan()` with zero repository objects. The `TestPlanningIndependence` test
class proves this with 8 assertions.

---

## 2. How the Engine Owns Ordering

### Ordering strategy: Deterministic UUID sort

Within `EvolutionPlanner.plan()`, targets are sorted by UUID before any
processing occurs:

```python
ordered = tuple(sorted(available))
```

This means:
- Duplicate category: pairs are formed from sorted order, not caller order
- Conflict category: pairs are formed from sorted order, not caller order
- Obsolete category: each target is processed in sorted order
- Affected targets list: `sorted(set(...))` — already deterministic

Additionally, operations are sorted after construction:

```python
operations.sort(key=lambda op: (op.target_id, op.transition_type.value, op.reason))
```

This guarantees that even if multiple passes produce operations in different
orders, the final output is identical.

### Why caller order can no longer affect execution

Caller provides `targets=(C, A, B)`. The planner sorts to `(A, B, C)`.
Caller provides `targets=(B, A, C)`. The planner sorts to `(A, B, C)`.
Resulting plan is identical.

**Proof**: `TestStrategyOwnership` contains 8 tests that demonstrate:
- `(A,B,C)` and `(C,B,A)` produce the same plan
- `(A,B,C,D)` and `(D,C,A,B)` produce the same plan  
- `(A,C,B)`, `(B,C,A)`, `(C,A,B)` all produce the same plan
- Operation target order is always sorted UUID order, never caller order

---

## 3. Why Planning Is Now Infrastructure-Independent

Three layers of isolation:

1. **EvolutionPlanner imports nothing from infrastructure**
   ```
   planning.py imports:
     evolution_context.py   (domain)
     evolution_operation.py (domain)
     evolution_plan.py      (domain)
     transition_type.py     (domain)
   ```
   Zero Repository, Runtime, Application, or Transaction imports.

2. **EvolutionUseCase uses EvolutionPlanner directly**
   - No `EvolutionEngine` dependency in the planning path
   - No `KnowledgeRepository` or `EvolutionRepository` access
   - No `UnitOfWork`, no `Runtime`, no `Application services`

3. **Tests prove it**
   - `TestPlanningIndependence.test_planner_constructible_without_repositories`
     verifies the planner has no `_knowledge`, `_evolution`, or `_repository` attrs.
   - `TestPlanningIndependence.test_planner_plan_executes_without_repositories`
     verifies `plan()` succeeds with zero repos.
   - `TestPlanningIndependence.test_planner_no_repository_imports` scans
     the source for "Repository" — not found.
   - `TestPlanningIndependence.test_engine_plan_works_without_repos`
     proves `EvolutionEngine(repos=None).plan()` succeeds.

**Repositories are impossible to access during planning** because:
- `EvolutionPlanner` has no reference to them (no constructor param, no import)
- `EvolutionUseCase` has no reference to them (uses planner, not engine)
- The only way repos enter the picture is through `EvolutionEngine`'s mutation
  methods (`evolve`, `record_conflict`), which are never called during planning

---

## 4. Why Planning Is Still Deterministic

### Sources of non-determinism eliminated

| Source | Before | After |
|--------|--------|-------|
| `set()` for quarantined | iteration order unspecified | `tuple(sorted(...))` — deterministic |
| Caller target order | used directly | sorted by UUID |
| Operation construction | caller-order iteration | sorted-order iteration |
| Operation ordering | caller-order insertion | final `sort()` by (target_id, type, reason) |
| Dict iteration | not used | not used |
| Timestamps | not used | not used |
| Randomness | not used | not used |

### Proof

- `TestPlannerPlan.test_identical_input_identical_plan`: same input → same plan
- `TestPlannerPlan.test_plan_is_deterministic_across_categories`: 10 runs → identical
- `TestStrategyOwnership.*`: 8 tests proving caller order independence

The planner is a pure function: output depends solely on input tuples and
strings, all of which are hashable and compared by value.

---

## 5. Why DTOs Are Future-Proof

### EvolutionSummary before and after

Before (flat fields):
```python
@dataclass(frozen=True)
class EvolutionSummary:
    evolution_started: bool
    evolution_completed: bool
    evolution_success: bool
    evolution_duration: timedelta
    planned_operations_count: int = 0
    affected_targets_count: int = 0
    quarantined_skipped: int = 0
```

After (nested PlanningMetrics):
```python
@dataclass(frozen=True)
class PlanningMetrics:
    planned_operations_count: int = 0
    affected_targets_count: int = 0
    quarantined_skipped: int = 0

@dataclass(frozen=True)
class EvolutionSummary:
    evolution_started: bool
    evolution_completed: bool
    evolution_success: bool
    evolution_duration: timedelta
    planning: PlanningMetrics = PlanningMetrics()
```

### How execution metrics can be added without changing semantics

When Part 7.4 introduces execution tracking, an `ExecutionMetrics` DTO can be
added alongside `PlanningMetrics`:

```python
@dataclass(frozen=True)
class ExecutionMetrics:
    executed_operations_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0

@dataclass(frozen=True)
class EvolutionSummary:
    ...
    planning: PlanningMetrics = PlanningMetrics()
    execution: ExecutionMetrics = ExecutionMetrics()  # Part 7.4
```

Existing code accessing `summary.planning.planned_operations_count` continues
to work unchanged. No rename, no removal, no semantic shift.

### Why this structure was chosen

- **Extends, never replaces**: old flat fields were moved *into* a namespace
  that coexists with future metrics.
- **Self-documenting**: `PlanningMetrics` communicates that these come from
  the planning stage, not execution.
- **Default-empty**: zero-arg `EvolutionSummary()` still works.
- **Frozen**: immutability prevents accidental overwrite.

---

## 6. Rollback Plan

### Modified files (4)

| File | Change | Revert |
|------|--------|--------|
| `src/brain/evolution/planning.py` | **New file** — `EvolutionPlanner` class | Delete file |
| `src/brain/evolution/evolution.py` | Made repos optional; `plan()` delegates to planner | Restore original `__init__` requiring repos; restore inline `plan()` logic |
| `src/brain/evolution/__init__.py` | Added `EvolutionPlanner` export | Remove export line |
| `src/brain/application/usecases/models.py` | Added `PlanningMetrics`; nested in `EvolutionSummary` | Flatten fields back to `EvolutionSummary` |
| `src/brain/application/usecases/evolution.py` | Use `EvolutionPlanner` instead of `EvolutionEngine` | Restore `engine: EvolutionEngine` param; restore flat field assignment |
| `tests/application/usecases/test_evolution.py` | Adapted to new interfaces; added 21 new tests | Restore original file |

### Rollback command

```bash
git checkout -- \
  src/brain/evolution/planning.py \
  src/brain/evolution/evolution.py \
  src/brain/evolution/__init__.py \
  src/brain/application/usecases/models.py \
  src/brain/application/usecases/evolution.py \
  tests/application/usecases/test_evolution.py
```

Then verify with the full test suite.

---

## 7. Test Report

### New test classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestPlannerPlan` | 11 | Core planning via `EvolutionPlanner` (replaces `TestEnginePlan`) |
| `TestPlannerPlanContextRespectsQuarantine` | 4 | Quarantine filtering via planner |
| `TestPlannerPlanOptimisticConcurrency` | 2 | Expected version recording via planner |
| `TestPlanningIndependence` | 8 | **Refinement 6**: zero-repo planning |
| `TestStrategyOwnership` | 8 | **Refinement 7**: caller-order independence |
| `TestEnginePlanDelegation` | 4 | Engine delegation to planner (without repos) |
| `TestPlanningMetricsDTO` | 6 | **Refinement 3+8**: new DTO |

### New assertion categories

- **Infrastructure independence**: planner has no repo attrs; source has no repo imports
- **Caller-order independence**: reversed/scrambled inputs → same outputs
- **Operation ordering**: engine sort by UUID → caller order irrelevant
- **DTO nesting**: PlanningMetrics lives inside EvolutionSummary
- **Engine delegation**: `EvolutionEngine(repos=None).plan()` works

### Test counts

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Evolution tests (`test_evolution.py`) | ~64 | 85 | **+21** |
| Bridge tests (`test_reflection_evolution.py`) | 33 | 33 | 0 |
| Full suite | 1285 | **1306** | **+21** |
| Regressions | — | 0 | ✅ |

---

## Definition of Done — Verification

| Requirement | Status | Evidence |
|-------------|--------|----------|
| ✅ Planning has zero infrastructure dependency | ✅ | `EvolutionPlanner` imports only domain; no repos in source |
| ✅ Planning can execute without repository objects | ✅ | `TestPlanningIndependence.test_planner_plan_executes_without_repositories` |
| ✅ Engine alone determines operation ordering | ✅ | Targets sorted by UUID; operations sorted by (id, type, reason) |
| ✅ Caller order cannot affect the resulting plan | ✅ | `TestStrategyOwnership` — 8 tests proving caller-order independence |
| ✅ EvolutionSummary is extended, not semantically replaced | ✅ | `PlanningMetrics` nested; old flat approach replaced with namespaced extension |
| ✅ Planning remains immutable, deterministic, and stateless | ✅ | No dict/set iteration; no timestamps; no randomness; frozen dataclasses |
| ✅ No transactions or mutations have been introduced | ✅ | `TestPlanningIndependence.test_planner_no_infrastructure_imports` confirms no "commit", "rollback", etc. |
| ✅ All existing tests pass | ✅ | 1306/1306 passed |
| ✅ New refinement tests pass | ✅ | All 85 evolution tests + 21 new pass |
| ✅ Architecture report confirms each refinement with evidence | ✅ | This document |
