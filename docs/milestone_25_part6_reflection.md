# Milestone 25 — Part 6: Reflection Integration

## 1. Directory Tree Changes

### Files Created
```
src/brain/application/maintenance/__init__.py
src/brain/application/maintenance/service.py        # ReflectionMaintenanceService
tests/application/maintenance/__init__.py
tests/application/maintenance/test_service.py       # Maintenance service tests
```

### Files Modified
```
src/brain/application/usecases/models.py             # +ReflectionRequest, +ReflectionSummary
src/brain/application/usecases/reflection.py         # Rewritten: engine+repository, execute(request)→ReflectionSummary
src/brain/runtime/runtime.py                         # +maintenance: ReflectionMaintenanceService
src/brain/runtime/factory.py                         # +ReflectionUseCase, +ReflectionMaintenanceService wiring
tests/application/usecases/test_reflection.py        # Rewritten for new constructor and execute(request) pattern
tests/runtime/test_runtime.py                        # +maintenance wiring checks
```

### Files NOT Modified
```
src/brain/reflection/*                               # Untouched
src/brain/learning/*                                 # Untouched
src/brain/execution/*                                # Untouched
src/brain/planning/*                                 # Untouched
src/brain/application/brain_session.py               # Untouched
src/brain/application/brain_service.py               # Untouched
src/brain/application/workflow/*                     # Untouched
```

## 2. Reflection Lifecycle

```
ReflectionRequest
    ↓
ReflectionMaintenanceService.reflect()
    ↓
ReflectionUseCase.execute()
    ↓
KnowledgeRepository.list_all_versions()
    ↓
ReflectionEngine.reflect(versions)
    ↓
ReflectionReport (internal)
    ↓
ReflectionSummary
```

## 3. Boundary Proof

### BrainWorkflow — Unchanged
BrainWorkflow does NOT import:
- `brain.reflection.*`
- `brain.application.maintenance.*`
- `brain.application.usecases.reflection.*`

BrainWorkflow remains focused on: Planning → Execution → Learning.

### Reflection Maintenance — Independent Path
```
Runtime.maintenance (ReflectionMaintenanceService)
    └── ReflectionUseCase
            └── ReflectionEngine
            └── KnowledgeRepository
```

Reflection is a separate cognitive path:
- Not triggered by task execution
- Not part of the workflow lifecycle
- Operates independently on knowledge

### DTO Boundary Preserved
- `ReflectionRequest`: scope, project, metadata — intent only
- `ReflectionSummary`: metrics only — no domain objects exposed
- `ReflectionUseCase` translates between DTOs and domain models internally
- `ReflectionMaintenanceService` only uses application-layer types

## 4. Dependency Proof

### Allowed Imports
```
ReflectionMaintenanceService
    → ReflectionUseCase          (application use case)
    → ReflectionRequest          (application DTO)
    → ReflectionSummary          (application DTO)

ReflectionUseCase
    → ReflectionEngine           (cognitive engine)
    → KnowledgeRepository        (repository interface)
    → ReflectionRequest          (application DTO)
    → ReflectionSummary          (application DTO)
    → ReflectionType             (domain enum — for counting)
```

### Forbidden Imports — Confirmed Absent
```
BrainWorkflow → brain.reflection.*          NOT IMPORTED
BrainWorkflow → brain.application.maintenance.*   NOT IMPORTED
BrainWorkflow → brain.application.usecases.reflection.*  NOT IMPORTED
```

### No Cycles
```
Runtime → BrainWorkflow (workflow path)
Runtime → ReflectionMaintenanceService (maintenance path)

These paths never cross.
BrainWorkflow never touches maintenance.
Maintenance never touches workflow.
```

## 5. Failure Behavior

### Reflection Failure
```
ReflectionUseCase.execute() raises exception
    → ReflectionMaintenanceService.reflect() propagates
    → Caller handles
    → BrainWorkflow completely unaffected
    → Execution results preserved
    → Learning results preserved
```

Reflection failure NEVER affects:
- Workflow execution
- Task results
- Knowledge updates from learning

### Runtime Failure
```
ReflectionEngine raises exception
    → ReflectionUseCase propagates
    → ReflectionMaintenanceService propagates
    → BrainRuntime.maintenance is still constructed
    → Only reflect() calls fail at runtime
```

## 6. Statelessness Proof

```
maintenance.reflect(request1) → summary1
maintenance.reflect(request2) → summary2
maintenance.reflect(request3) → summary3
```

- Each call creates fresh versions list from repository
- Each call invokes engine independently
- No cached state between calls
- ReflectionUseCase is frozen — no mutable state

## 7. Rollback Verification

Reverting Part 6 requires reverting ONLY:
```
src/brain/application/maintenance/__init__.py        # DELETE
src/brain/application/maintenance/service.py          # DELETE
src/brain/application/usecases/models.py              # Remove ReflectionRequest, ReflectionSummary
src/brain/application/usecases/reflection.py          # Revert to Part 5 version
src/brain/runtime/runtime.py                          # Remove maintenance field
src/brain/runtime/factory.py                          # Remove ReflectionUseCase, ReflectionMaintenanceService wiring
tests/application/maintenance/__init__.py             # DELETE
tests/application/maintenance/test_service.py          # DELETE
tests/application/usecases/test_reflection.py          # Revert to Part 5 version
tests/runtime/test_runtime.py                          # Remove maintenance wiring checks
```

NOT required:
- `src/brain/reflection/*` — untouched
- `src/brain/learning/*` — untouched
- `src/brain/execution/*` — untouched
- `src/brain/planning/*` — untouched
- `src/brain/application/workflow/*` — untouched
- `src/brain/application/brain_session.py` — untouched
- `src/brain/application/brain_service.py` — untouched

## Architecture After Part 6

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
```

Two independent cognitive paths:
1. **Task Execution**: Planning → Execution → Learning (via BrainWorkflow)
2. **Knowledge Maintenance**: Reflection (via BrainMaintenance / ReflectionMaintenanceService)

These paths never intersect. They share the same repository but operate independently.

## Test Summary
- **1199 tests passing** (was 1171 before Part 6)
- 28 new tests across reflection use case, maintenance service, and runtime wiring
- Boundary isolation verified
- Failure isolation verified
- Statelessness verified
