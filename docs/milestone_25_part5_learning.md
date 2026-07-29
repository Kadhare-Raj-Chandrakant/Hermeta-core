# Milestone 25 — Part 5: Learning Integration

## 1. Directory Tree Changes

### Files Created
```
src/brain/application/bridges/__init__.py
src/brain/application/bridges/execution_learning.py    # ExecutionLearningMapper
tests/application/bridges/__init__.py
tests/application/bridges/test_execution_learning.py   # Mapper tests
```

### Files Modified
```
src/brain/application/usecases/models.py               # +LearningRequest, +LearningSummary
src/brain/application/usecases/learning.py              # +execute_learning(), +_request_to_observations()
src/brain/application/workflow/workflow.py              # +learning, +mapper in constructor; learning phase in run()
src/brain/application/workflow/report.py                # +6 learning fields
src/brain/runtime/factory.py                            # +LearningUseCase, +ExecutionLearningMapper wiring
tests/application/usecases/test_learning.py             # Rewritten with execute_learning tests
tests/application/test_workflow.py                      # Rewritten with learning integration
tests/runtime/test_runtime.py                           # Updated with learning/mapper wiring
```

### Files NOT Modified
```
src/brain/learning/coordinator.py                       # Untouched
src/brain/learning/execution_feedback.py                # Untouched
src/brain/learning/report.py                            # Untouched
src/brain/execution/*                                   # Untouched
src/brain/planning/*                                    # Untouched
src/brain/detection/observation.py                      # Untouched
src/brain/application/brain_session.py                  # Untouched
src/brain/application/brain_service.py                  # Untouched
```

## 2. Complete Cognitive Lifecycle

```
AdapterTask
    ↓
BrainWorkflow.run(task)
    ↓
BrainSession.begin(domain_task)
    ↓
PlanningRequest
    ↓
PlanningUseCase.execute_request()
    ↓
PlanningSummary
    ↓
ExecutionRequest
    ↓
ExecutionUseCase.execute()
    ↓
ExecutionSummary
    ↓
ExecutionLearningMapper.from_execution()
    ↓
LearningRequest
    ↓
LearningUseCase.execute_learning()
    ↓
LearningSummary
    ↓
BrainSession.complete()
    ↓
WorkflowReport
```

## 3. Boundary Proof

### BrainWorkflow Imports
```python
from brain.adapter.models import AdapterTask
from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.brain_session import BrainSession
from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.models import ExecutionRequest, PlanningRequest
from brain.application.usecases.planning import PlanningUseCase
from brain.application.workflow.report import WorkflowReport
from brain.domain.task import Priority, Task
```

**Forbidden imports ABSENT:**
- `brain.learning.*` — not imported
- `brain.execution.*` — not imported
- `brain.planning.*` (engines, strategies, goals, actions) — not imported
- `brain.reflection.*` — not imported
- `brain.evolution.*` — not imported
- `brain.detection.*` — not imported

### ExecutionLearningMapper Imports
```python
from brain.application.usecases.models import ExecutionSummary, LearningRequest
```
Pure DTO→DTO. No engine, repository, or domain model imports.

### Translation Responsibility Chain
- **BrainWorkflow**: Orchestrates stages, passes DTOs between use cases. No translation.
- **ExecutionLearningMapper**: Translates ExecutionSummary → LearningRequest. Pure DTO conversion.
- **LearningUseCase**: Translates LearningRequest → Observation (for coordinator). DTO→domain translation at the boundary.

## 4. Dependency Proof

```
BrainWorkflow
    ├── PlanningUseCase    → PlanningEngine
    ├── ExecutionUseCase   → ExecutionEngine → PlanningUseCase
    ├── LearningUseCase    → LearningCoordinator
    └── ExecutionLearningMapper  (no dependencies)
```

Forbidden direct dependencies ABSENT:
- `BrainWorkflow → LearningCoordinator` — not connected
- `BrainWorkflow → ExecutionReport` — not connected
- `BrainWorkflow → Observation` — not connected

## 5. Failure Behavior

### Planning Failure
```
PlanningUseCase raises exception
    → Execution skipped (not called)
    → Learning skipped (not called)
    → Session cleanup
    → WorkflowReport: success=False, all metrics zero
```

### Execution Failure
```
ExecutionUseCase raises exception
    → Learning skipped (never reached)
    → Session cleanup
    → WorkflowReport: success=False, execution metrics zero
```

### Learning Failure
```
LearningUseCase raises exception
    → Caught by inner try/except
    → Session complete() still called
    → WorkflowReport: success=True, execution metrics PRESERVED, learning metrics zero
    → learning_performed=False
```

Key: Learning failure does NOT corrupt execution results. The workflow still reports success because execution succeeded.

## 6. Statelessness Proof

```
workflow.run(task)  → report1 (session_id=UUID-A)
workflow.run(task)  → report2 (session_id=UUID-B)
workflow.run(task)  → report3 (session_id=UUID-C)
```

- Each run generates a unique `session_id`
- Session is `begin()` → `complete()` per run (no state leakage)
- Learning use case creates fresh observations per call
- No cached state between runs

## 7. Rollback Proof

Reverting Part 5 requires reverting ONLY:
```
src/brain/application/bridges/__init__.py              # DELETE
src/brain/application/bridges/execution_learning.py     # DELETE
src/brain/application/usecases/models.py               # Remove LearningRequest, LearningSummary
src/brain/application/usecases/learning.py              # Remove execute_learning, _request_to_observations
src/brain/application/workflow/workflow.py              # Remove learning/mapper from constructor and run()
src/brain/application/workflow/report.py                # Remove 6 learning fields
src/brain/runtime/factory.py                            # Remove LearningUseCase, ExecutionLearningMapper wiring
tests/application/bridges/__init__.py                   # DELETE
tests/application/bridges/test_execution_learning.py    # DELETE
tests/application/usecases/test_learning.py             # Revert to Part 4 version
tests/application/test_workflow.py                      # Revert to Part 4 version
tests/runtime/test_runtime.py                           # Remove learning/mapper wiring checks
```

NOT required:
- `src/brain/learning/coordinator.py` — untouched
- `src/brain/learning/execution_feedback.py` — untouched
- `src/brain/execution/*` — untouched
- `src/brain/planning/*` — untouched
- `src/brain/application/brain_session.py` — untouched

## 8. Readiness for Part 6 (Reflection Integration)

The architecture extends naturally:

```
ExecutionSummary
    ↓
ExecutionReflectionMapper  (new bridge)
    ↓
ReflectionRequest          (new DTO)
    ↓
ReflectionUseCase          (new use case)
    ↓
ReflectionSummary          (new DTO)
    ↓
WorkflowReport             (extended)
```

No modifications required to:
- LearningCoordinator
- ExecutionEngine
- PlanningEngine
- BrainWorkflow architecture (only add new constructor param + stage)

The pattern is now established:
1. Create application DTOs (Request + Summary)
2. Create a bridge mapper (DTO→DTO)
3. Create a use case (DTO→domain→DTO)
4. Add to BrainWorkflow constructor and run()
5. Add metrics to WorkflowReport
6. Wire in Runtime factory

## Test Summary
- **1171 tests passing** (was 1108 before Part 5)
- 63 new tests across learning use case, mapper, and workflow
- Boundary isolation verified with 18 import-prohibition tests
- Failure semantics verified for all 3 failure modes
