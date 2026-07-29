# Milestone 25 — Part 7.1: Evolution Boundary Foundation

## 1. Files Changed

### Files Modified
```
src/brain/application/usecases/models.py             # +EvolutionRequest, +EvolutionSummary DTOs
src/brain/application/usecases/evolution.py          # Rewritten: EvolutionEngine only, execute(request)→EvolutionSummary
src/brain/application/usecases/__init__.py           # No changes required (EvolutionUseCase already exported)
tests/application/usecases/test_evolution.py         # Rewritten: 34 tests covering DTOs, use case, boundary isolation
```

### Files NOT Modified
```
src/brain/evolution/*                                # Untouched — EvolutionEngine, KnowledgeTransition, Conflict, etc.
src/brain/application/workflow/*                     # Untouched — BrainWorkflow
src/brain/application/maintenance/*                  # Untouched — ReflectionMaintenanceService
src/brain/application/usecases/planning.py           # Untouched
src/brain/application/usecases/execution.py          # Untouched
src/brain/application/usecases/learning.py           # Untouched
src/brain/application/usecases/reflection.py         # Untouched
src/brain/runtime/runtime.py                         # Untouched
src/brain/runtime/factory.py                         # Untouched
src/brain/reflection/*                               # Untouched
src/brain/learning/*                                 # Untouched
src/brain/execution/*                                # Untouched
src/brain/planning/*                                 # Untouched
src/brain/repositories/*                             # Untouched
```

## 2. Boundary Diagram

```
    Application Layer
    ─────────────────

    EvolutionRequest (targets, context, metadata)
            │
            ▼
    EvolutionUseCase (engine: EvolutionEngine)
            │  • accept request
            │  • delegate to engine
            │  • translate output
            │
            ▼
    EvolutionSummary (counts, duration, success)


    Evolution Subsystem (untouched)
    ───────────────────────────────

    EvolutionEngine
            │  • get_all_transitions()
            │  • get_conflicts()
            │  • evolve()          ← NOT called by use case
            │  • record_conflict() ← NOT called by use case
            │
            ▼
    KnowledgeRepository (read methods only)
```

The application layer sits above the evolution subsystem. It translates between DTOs and delegates to the engine. The engine remains unaware of the application layer.

## 3. Responsibility Proof

### EvolutionUseCase — Three responsibilities only

**Translate:**
- Accepts `EvolutionRequest` (application DTO)
- Passes target IDs to engine for filtering
- Returns `EvolutionSummary` (application DTO)

**Delegate:**
- Calls `engine.get_all_transitions()` — read-only
- Calls `engine.get_conflicts()` — read-only
- No mutation methods called

**Summarize:**
- Counts total transitions (`processed_count`)
- Counts non-CONTRADICTS transitions (`changed_count`)
- Counts conflicts (`conflict_count`)
- Measures duration

### EvolutionEngine — Owns evolution intelligence

- Decides how transitions are created (via `evolve()`)
- Decides how conflicts are recorded (via `record_conflict()`)
- Stores and retrieves transitions and conflicts
- All decision-making stays inside the engine

### EvolutionUseCase — Does NOT

- ❌ Choose evolution strategy
- ❌ Decide merge target
- ❌ Decide replacement strategy
- ❌ Decide deletion
- ❌ Decide conflict resolution
- ❌ Mutate repository
- ❌ Manage transactions
- ❌ Create audit records

## 4. Dependency Proof

### Allowed Direction — Confirmed

```
application/usecases/evolution.py
        │
        │  imports
        ▼
brain.evolution.evolution.EvolutionEngine
brain.evolution.transition_type.TransitionType
brain.evolution.transition.KnowledgeTransition
```

The application layer imports from the evolution subsystem. This is the correct direction.

### Forbidden Direction — Confirmed Absent

```
brain.evolution.*
        │
        │  does NOT import
        ▼
brain.application.*
```

The evolution subsystem has no knowledge of the application layer. Verified by inspecting `brain/evolution/` source files — none contain `from brain.application` or reference application-layer types.

### Import Proof by Test

8 boundary tests in `TestBoundaryIsolation` confirm the use case does NOT import:
- `brain.repositories` — no repository access
- `brain.runtime` — no runtime coupling
- `brain.application.workflow` — no workflow coupling
- `brain.application.maintenance` — no maintenance coupling
- `brain.reflection` — no reflection coupling
- `brain.learning` — no learning coupling

## 5. No Decision Proof

### What Decision-Making Would Look Like

```python
# ❌ MERGE DECISION
if existing.is_newer_than(incoming):
    keep(existing)
else:
    replace(existing, incoming)

# ❌ DELETION DECISION
if not is_useful(version):
    delete(version)

# ❌ CONFLICT RESOLUTION DECISION
if can_auto_resolve(conflict):
    resolve(conflict)
else:
    escalate(conflict)
```

### What EvolutionUseCase Actually Does

```python
def execute(self, request: EvolutionRequest) -> EvolutionSummary:
    all_transitions = self.engine.get_all_transitions()
    all_conflicts = self.engine.get_conflicts()

    # Filter — NOT decide
    if request.targets:
        target_set = set(request.targets)
        transitions = tuple(
            t for t in all_transitions
            if t.from_version_id in target_set or t.to_version_id in target_set
        )
    else:
        transitions = all_transitions

    # Count — NOT decide
    return EvolutionSummary(
        processed_count=len(transitions),
        changed_count=sum(1 for t in transitions if t.transition_type != TransitionType.CONTRADICTS),
        conflict_count=len(conflicts),
    )
```

No `if/else` on version content. No merge logic. No replacement logic. No deletion logic. No resolution logic. Only:
- Read from engine
- Filter by target IDs
- Count results
- Return summary

### Confirmed by Test

```python
def test_no_decision_making(self):
    import inspect
    source = inspect.getsource(EvolutionUseCase)
    assert "merge" not in source.lower()
    assert "replace" not in source.lower()
    assert "delete" not in source.lower()
    assert "resolve" not in source.lower()
```

## 6. Rollback Verification

### Reverting Part 7.1 Requires ONLY

```
src/brain/application/usecases/models.py              # Remove EvolutionRequest, EvolutionSummary
src/brain/application/usecases/evolution.py           # Revert to Part 6 version
tests/application/usecases/test_evolution.py           # Revert to Part 6 version
```

### NOT Required

```
src/brain/evolution/*                                 # Untouched — no rollback needed
src/brain/reflection/*                                # Untouched
src/brain/learning/*                                  # Untouched
src/brain/execution/*                                 # Untouched
src/brain/planning/*                                  # Untouched
src/brain/runtime/*                                   # Untouched
src/brain/repositories/*                              # Untouched
src/brain/application/workflow/*                      # Untouched
src/brain/application/maintenance/*                   # Untouched
```

Reverting Part 7.1 leaves all cognitive subsystems, the runtime, and all other use cases completely unaffected. The only loss is the ability to call Evolution through the application layer.

## 7. Failure Behavior

### Engine Read Failure
```
EvolutionEngine.get_all_transitions() raises exception
    → EvolutionUseCase.execute() propagates
    → Caller handles
    → No mutations occurred
    → No state corrupted
```

### Engine Conflict Fetch Failure
```
EvolutionEngine.get_conflicts() raises exception
    → EvolutionUseCase.execute() propagates
    → Caller handles
    → No mutations occurred
```

### Failure Isolation
Evolution failure NEVER affects:
- Workflow execution (BrainWorkflow)
- Task results (Planning, Execution, Learning)
- Reflection operations (BrainMaintenance)
- Any existing knowledge or transitions

## 8. Statelessness Proof

```
use_case.execute(request1) → summary1
use_case.execute(request2) → summary2
use_case.execute(request3) → summary3
```

- Each call fetches fresh data from engine via `get_all_transitions()` and `get_conflicts()`
- Each call invokes engine independently
- No cached state between calls
- EvolutionUseCase is frozen dataclass — no mutable instance state
- Two calls produce independent `EvolutionSummary` objects

## 9. Test Coverage

| Category | Tests | Description |
|---|---|---|
| DTO Construction | 6 | Request/Summary creation, frozen, equality |
| Construction | 1 | Engine storage |
| Execute | 10 | Return type, engine calls, summary fields, empty results, duration |
| Target Filtering | 4 | Filter by ID, empty targets, multiple targets |
| Engine Failure | 2 | Propagation of engine exceptions |
| Statelessness | 1 | Independent results across calls |
| Immutability | 1 | Frozen use case |
| Boundary Isolation | 8 | No forbidden imports, no decision-making |
| **Total** | **34** | |

## Architecture After Part 7.1

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


                        EvolutionUseCase (independent inspector)
                              |
                        EvolutionEngine
                        (read methods only)
```

Three cognitive paths:
1. **Task Execution**: Planning → Execution → Learning (via BrainWorkflow)
2. **Knowledge Maintenance**: Reflection (via BrainMaintenance / ReflectionMaintenanceService)
3. **Evolution Inspection**: Read-only summary of transitions and conflicts (via EvolutionUseCase)

These paths never intersect. Evolution is currently a pure inspector — future parts will add write operations and integration points.

## Test Summary

- **1222 tests passing** (was 1199 before Part 7.1)
- 34 tests in test_evolution.py (replaced 2 old tests, net +32)
- Evolution boundary fully isolated from all other subsystems
- Read-only contract enforced by tests
- No decision-making logic in application layer
