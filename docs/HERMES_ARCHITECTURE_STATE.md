# Hermes Architecture State

## Vision

Hermes is a persistent AI brain designed to preserve understanding, memory, learning, reflection, and evolution across model changes. It treats knowledge as a living artifact: detected from raw observations, validated against completeness and confidence rules, persisted as versioned knowledge, and continuously refined through planning, execution, learning, reflection, and evolution cycles.

The architecture enforces strict separation between pure cognitive reasoning (engines), coordination and orchestration (use cases, workflow), and persistence (repositories). This separation ensures that each layer can be tested, reasoned about, and evolved independently without destabilizing the system.

---

## Completed Milestones

### Foundation / Domain Models
- Core domain: `brain/domain/` — `Task`, `Version`, `Identity`, `Enums`, `References`, `Understanding`
- Pure data structures with no external dependencies

### Knowledge Representation
- Versioned knowledge with `KnowledgeType`, `Evidence`, `References`, lifecycle tracking

### BrainService
- `brain/application/brain_service.py` — top-level knowledge ingestion and retrieval service
- Wraps pipeline, validation, compilation, relevance scoring, selection

### BrainSession
- `brain/application/brain_session.py` — workflow lifecycle, knowledge acquisition, compilation, service access

### Persistence Layer
- `brain/repositories/` — `base.py` (abstract `KnowledgeRepository`), `memory.py` (in-memory impl)
- `brain/repositories/evolution_base.py` — abstract `EvolutionRepository`
- `brain/infrastructure/sqlite/` — SQLite-backed repository implementation

### Pipeline
- `brain/pipeline/` — `Candidate`, `Evidence`, `Events`, `Validator`, `VersionCreator`
- Transforms raw observations into versioned knowledge candidates

### Planning
- `brain/planning/` — `PlanningEngine`, `PlanningStrategy`, `Goal`, `Action`, `Dependency`, `Blocked`, `Context`, `Plan`
- Pure, deterministic planning engine with zero application or repository dependencies

### Execution
- `brain/execution/` — `Executor`, `Observer`, `Policy`, `Context`, `Record`, `Report`, `Result`, `Status`, `Errors`, `Handlers`
- Executes plans via handler registry

### Learning
- `brain/learning/` — `LearningCoordinator`, `ExecutionFeedback`, `ReflectionBridge`, `Report`
- Coordinates detection, validation, knowledge persistence, and reflection

### Reflection
- `brain/reflection/` — `ReflectionEngine`, `Detector`, `Report`, `Finding`, `Type`
- Pure engine for analyzing knowledge structure and detecting gaps, conflicts, duplicates, obsolescence

### Evolution
- `brain/evolution/` — `EvolutionPlanner`, `EvolutionExecutor`, `EvolutionRecord`, `EvolutionPlan`, `EvolutionOperation`, `EvolutionContext`, `Transition`, `TransitionType`, `Conflict`
- Pure planning + transactional execution via `EvolutionUseCase`

### Milestone 25 Components
- **Workflow orchestration boundary** — `BrainWorkflow` (`brain/application/workflow/`)
- **Application use cases** — `brain/application/usecases/` (planning, execution, learning, reflection, evolution)
- **Planning integration** — `PlanningUseCase` orchestrates `PlanningEngine`
- **Execution integration** — `ExecutionUseCase` orchestrates `Executor`
- **Learning integration** — `LearningUseCase` orchestrates `LearningCoordinator`
- **Reflection maintenance path** — `ReflectionUseCase`, `ReflectionMaintenanceService`
- **Evolution planning** — `EvolutionPlanner` in `brain/evolution/planning.py`
- **Evolution transactional execution** — `EvolutionExecutor`, `EvolutionUnitOfWork`, `EvolutionUseCase`

---

## Current Architecture

### Layer Hierarchy

```
Application Layer
  brain.application.*
      │
      ▼
Cognitive Layer (Engines)
  brain.planning.*
  brain.reflection.*
  brain.evolution.*
  brain.learning.*
  brain.validation.*
  brain.detection.*
  brain.retrieval.*
  brain.services.*
  brain.execution.*
      │
      ▼
Infrastructure Layer
  brain.repositories.*
  brain.infrastructure.*
  brain.domain.*
```

### Main Runtime Paths

**Task Path:**
```
Adapter
  │
  ▼
BrainWorkflow
  │
  ▼
PlanningUseCase
  │
  ▼
ExecutionUseCase
  │
  ▼
LearningUseCase
```

**Maintenance Path:**
```
BrainMaintenance
  │
  ▼
ReflectionUseCase
  │
  ▼
ReflectionEngine
```

**Evolution Path:**
```
Reflection Finding
  │
  ▼
ReflectionEvolutionBridge
  │
  ▼
EvolutionRequest
  │
  ▼
EvolutionPlanner
  │
  ▼
EvolutionPlan
  │
  ▼
EvolutionUseCase
  │
  ├── EvolutionUnitOfWork.begin()
  │
  ▼
EvolutionExecutor
  │
  ▼
commit() / rollback()
  │
  ▼
EvolutionSummary
```

### Module Map

| Module | Type | Dependencies | Description |
|--------|------|-------------|-------------|
| `brain.domain` | Domain | none | Pure data models (Task, Version, Identity, etc.) |
| `brain.repositories` | Infrastructure | `brain.domain` | Abstract persistence contracts + in-memory impl |
| `brain.infrastructure.sqlite` | Infrastructure | `brain.repositories`, `brain.domain`, `brain.evolution` | SQLite-backed persistence |
| `brain.planning` | Engine | `brain.domain` | Pure planning engine |
| `brain.reflection` | Engine | `brain.domain` | Pure reflection engine |
| `brain.evolution.planning` | Engine | `brain.evolution`, `brain.domain` | Pure evolution planner |
| `brain.evolution.executor` | Engine | `brain.evolution`, `brain.repositories`, `brain.domain` | Plan executor (repositories for mutation only) |
| `brain.validation` | Engine | `brain.pipeline`, `brain.domain` | Validation engine |
| `brain.detection` | Engine | `brain.pipeline`, `brain.domain` | Observation detection |
| `brain.retrieval` | Engine | `brain.domain` | Knowledge retrieval |
| `brain.services` | Engine | `brain.domain`, `brain.retrieval` | Relevance, scoring, selection |
| `brain.execution` | Engine | `brain.planning`, `brain.domain` | Plan execution engine |
| `brain.learning` | Engine/Coordinator | `brain.detection`, `brain.validation`, `brain.application.brain_service`, `brain.reflection`, `brain.events`, `brain.execution` | Learning coordination |
| `brain.events` | Infrastructure | `brain.domain` | Event system |
| `brain.application.usecases` | Application | engines + repositories | Orchestration layer |
| `brain.application.workflow` | Application | use cases + adapters | Workflow orchestration |
| `brain.application.bridges` | Application | use case models | Data translation bridges |
| `brain.pipeline` | Infrastructure | `brain.domain` | Candidate processing pipeline |
| `brain.adapter` | Adapter | `brain.application`, `brain.domain` | External interface adapter |
| `brain.runtime` | Runtime | all layers | Factory, wiring, health |

---

## Architectural Laws

1. **Engines never depend on application layer.** Pure engines (`brain.planning.*`, `brain.reflection.*`, `brain.evolution.planning`, `brain.evolution.executor`, `brain.validation.*`, `brain.detection.*`, `brain.retrieval.*`, `brain.services.*`) must never import `brain.application.*`.

2. **UseCases orchestrate but do not contain cognitive strategy.** Use cases may call engines, translate DTOs, and manage transaction boundaries, but must never implement domain reasoning or algorithmic strategy.

3. **BrainWorkflow does not create planning domain objects.** `BrainWorkflow` orchestrates use case invocations and report generation. It must not construct `Goal`, `Action`, `Plan`, or other planning domain objects.

4. **Planning is pure and deterministic.** `PlanningEngine` and `PlanningStrategy` must have zero side effects, zero repository dependencies, and produce deterministic output for identical input.

5. **EvolutionPlanner creates intent only.** `EvolutionPlanner` produces an immutable `EvolutionPlan`. It must never execute operations or persist anything.

6. **EvolutionExecutor executes plans only.** `EvolutionExecutor` applies pre-computed plan operations in exact order. It must never create, mutate, or reorder plans.

7. **EvolutionUseCase owns transaction boundaries.** Only `EvolutionUseCase` may call `EvolutionUnitOfWork.begin()`, `.commit()`, `.rollback()`. Neither `EvolutionExecutor` nor repositories control transactions.

8. **Repository owns persistence primitives only.** Repositories expose low-level operations (`get_version`, `replace_version`, `save_transition`, `snapshot`, `restore`, etc.). They never receive domain objects like `EvolutionPlan`, `EvolutionRequest`, or `EvolutionContext`.

9. **Bridges translate data only and never make decisions.** Bridges (e.g., `ReflectionEvolutionBridge`) convert between component DTOs without applying strategy, filtering, or policy.

10. **No subsystem should bypass its application boundary.** Code in one layer must not import or call code that bypasses the intended layer hierarchy (e.g., engines must not import `BrainWorkflow`; use cases must not directly call repository mutation methods from within strategy logic).

---

## Ownership Rules

| State Component | Owner | Responsibility |
|----------------|-------|---------------|
| Workflow lifecycle | `BrainSession` | Start, manage, and complete workflow executions |
| Planning decisions | `PlanningEngine` | Goal construction, action sequencing, dependency resolution |
| Evolution strategy/ordering | `EvolutionPlanner` | Plan creation, operation ordering, quarantine decisions |
| Transaction lifecycle | `EvolutionUseCase` | uow.begin(), uow.commit(), uow.rollback() |
| Knowledge mutation | `EvolutionExecutor` | Apply evolution operations to repository |
| Evolution history | `EvolutionRepository` | Persist transitions, execution records |
| Failure/quarantine context | `EvolutionContext` | Track attempt counts, quarantined targets |

---

## Current Status

- **Test count:** 1348 passing (full suite)
- **Current phase:** Milestone 25 Stabilization
- **Active task:** Stabilization Part A.2 — Dependency Direction Audit

---

## Future Rules

Before implementing any future milestone:

1. Read this document.
2. Preserve architectural laws.
3. Avoid introducing new layers without justification.
4. Prefer small incremental changes.
5. Update this document if architecture genuinely changes.
