# Milestone 25 — Part 7.2: Reflection → Evolution Target Bridge

## 1. Directory Changes

### Files Created
```
src/brain/application/bridges/__init__.py              # Package init, exports ReflectionEvolutionBridge
src/brain/application/bridges/reflection_evolution.py  # ReflectionEvolutionBridge implementation
tests/application/bridges/__init__.py                  # Test package init
tests/application/bridges/test_reflection_evolution.py # 33 tests: construction, translation, determinism, boundary
```

### Files Modified
```
src/brain/application/usecases/models.py               # +FindingType enum, +ReflectionFindingDTO
```

### Files NOT Modified
```
src/brain/reflection/*                                 # Untouched — ReflectionEngine, ReflectionFinding, etc.
src/brain/evolution/*                                  # Untouched — EvolutionEngine
src/brain/application/workflow/*                       # Untouched — BrainWorkflow
src/brain/application/maintenance/*                    # Untouched — ReflectionMaintenanceService
src/brain/application/usecases/evolution.py            # Untouched — EvolutionUseCase
src/brain/application/usecases/reflection.py           # Untouched — ReflectionUseCase
src/brain/runtime/*                                    # Untouched
src/brain/repositories/*                               # Untouched
```

## 2. Translation Flow

```
ReflectionFindingDTO (application DTO)
        │
        │  finding_type, affected_versions, explanation, confidence
        │
        ▼
ReflectionEvolutionBridge.translate()
        │
        │  • targets ← affected_versions
        │  • context ← finding_type.value
        │  • metadata ← ("source","reflection"), ("confidence",…)
        │
        ▼
EvolutionRequest (application DTO)
        │
        │  targets, context, metadata
        │
        ▼
EvolutionUseCase.execute()
        │
        ▼
EvolutionEngine (decides resolution strategy)
```

## 3. Responsibility Proof

### Bridge owns

**Translation:**
- Converts `ReflectionFindingDTO` → `EvolutionRequest`
- Maps `FindingType` enum values to context strings
- Preserves `affected_versions` as `targets`

**Classification:**
- DUPLICATE → `"duplicate"`
- CONFLICT → `"conflict"`
- OBSOLETE → `"obsolete"`
- GAP → `"gap"`

**Metadata preservation:**
- Attaches `("source", "reflection")` — origin tracking
- Attaches `("confidence", …)` — finding confidence preserved

### Bridge does not own

- ❌ Strategy selection (merge/replace/delete)
- ❌ Conflict resolution
- ❌ Repository mutation
- ❌ Engine invocation
- ❌ Transaction management
- ❌ Decision making of any kind

### Proof

The bridge output is always an `EvolutionRequest` — a pure data carrier with `targets`, `context`, and `metadata`. No action, strategy, or resolution field exists on the DTO. The bridge never decides what to do with the findings; it only reports what was found and where.

## 4. Dependency Proof

### Allowed Direction — Confirmed

```
application/bridges/reflection_evolution.py
        │
        │  imports
        ▼
application/usecases/models.py
    (EvolutionRequest, FindingType, ReflectionFindingDTO)
```

The bridge depends only on application-layer DTOs. No subsystem imports.

### Forbidden Directions — Confirmed Absent

```
bridge → brain.evolution.evolution        NOT IMPORTED
bridge → brain.evolution.transition_type  NOT IMPORTED
bridge → brain.reflection.engine          NOT IMPORTED
bridge → brain.reflection.finding         NOT IMPORTED
bridge → brain.reflection.type            NOT IMPORTED
bridge → brain.repositories               NOT IMPORTED
bridge → brain.runtime                    NOT IMPORTED
bridge → brain.application.workflow       NOT IMPORTED
bridge → brain.application.maintenance    NOT IMPORTED
bridge → brain.learning                   NOT IMPORTED
```

### Import Proof by Test

9 boundary tests in `TestBoundaryIsolation` confirm the bridge does NOT import any subsystem or infrastructure module. 1 additional test confirms all DTOs originate from `application.usecases.models`.

## 5. Determinism Proof

```python
bridge.translate(finding_A) → request_1
bridge.translate(finding_A) → request_2
assert request_1 == request_2
```

The bridge:
- Has no mutable state (frozen dataclass, no instance variables)
- Performs no time-dependent operations
- Performs no random operations
- Performs no I/O
- Same input always produces identical output

Verified by test: `test_repeated_calls_equivalent` calls `translate()` 10 times with the same input and asserts all outputs are equal.

## 6. Rollback Verification

### Reverting Part 7.2 requires ONLY

Delete:
```
src/brain/application/bridges/__init__.py
src/brain/application/bridges/reflection_evolution.py
tests/application/bridges/__init__.py
tests/application/bridges/test_reflection_evolution.py
```

Revert:
```
src/brain/application/usecases/models.py    # Remove FindingType, ReflectionFindingDTO
```

### NOT Required

```
src/brain/reflection/*                      # Untouched
src/brain/evolution/*                       # Untouched
src/brain/application/workflow/*            # Untouched
src/brain/application/maintenance/*         # Untouched
src/brain/application/usecases/evolution.py # Untouched
src/brain/application/usecases/reflection.py # Untouched
src/brain/runtime/*                         # Untouched
src/brain/repositories/*                    # Untouched
```

No cognitive subsystem is affected by reverting Part 7.2.

## 7. Failure Behavior

The bridge has no failure modes. It:
- Performs no I/O
- Accesses no repositories
- Calls no engines
- Validates no preconditions beyond frozen dataclass construction

The only possible failure is constructing a `ReflectionFindingDTO` with invalid data (e.g., confidence out of range), which is validated by the DTO's own constraints — not the bridge.

## 8. Statelessness Proof

```
bridge.translate(finding) → request_1
bridge.translate(finding) → request_2
bridge.translate(finding) → request_3
```

- Each call reads from the input finding (immutable)
- Each call produces a fresh `EvolutionRequest`
- No cached state between calls
- Bridge is frozen — no mutable instance state

## 9. Test Coverage

| Category | Tests | Description |
|---|---|---|
| Construction | 3 | Creation, no dependencies, frozen |
| Translation | 11 | All 4 finding types, targets, category, metadata |
| No Decision Leakage | 7 | No action/strategy/resolution in output |
| Determinism | 2 | Same input same output, repeated calls |
| Boundary Isolation | 10 | No forbidden imports, DTO-only dependency |
| **Total** | **33** | |

## Architecture After Part 7.2

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


                   ReflectionEvolutionBridge (independent translator)
                          |                    |
                ReflectionFindingDTO    EvolutionRequest
                (application DTO)       (application DTO)


                   EvolutionUseCase (independent inspector)
                          |
                    EvolutionEngine
                    (read methods only)
```

Four independent application-layer components:
1. **BrainWorkflow** — Planning → Execution → Learning
2. **BrainMaintenance** — Reflection via ReflectionUseCase
3. **ReflectionEvolutionBridge** — Translates reflection outputs to evolution requests
4. **EvolutionUseCase** — Read-only inspection of evolution state

The bridge sits between reflection and evolution as a pure translation layer. It does not connect them — it only converts data formats. The actual connection (reflection triggering evolution) will be implemented in later parts.

## Test Summary
- **1255 tests passing** (was 1222 before Part 7.2)
- 33 new tests across construction, translation, determinism, and boundary isolation
- Bridge is fully decoupled from all subsystems
- Zero decision-making logic in translation layer
- Determinism verified across repeated calls
