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

## Public Contract Ownership

The following contracts define the public architectural boundaries of Hermes. These are the interfaces that layers are allowed to depend on.

| Contract | Owner | Consumers | Description |
|----------|-------|-----------|-------------|
| `KnowledgeIngestionPort` | `BrainService` (implements) | `LearningCoordinator`, `BrainSession`, `BrainAdapter` | Knowledge persistence contract |
| `PlanningUseCase` | `brain.application.usecases.planning` | `BrainWorkflow` | Planning orchestration (DTO in/out) |
| `ExecutionUseCase` | `brain.application.usecases.execution` | `BrainWorkflow` | Execution orchestration (DTO in/out) |
| `LearningUseCase` | `brain.application.usecases.learning` | `BrainWorkflow` | Learning orchestration (DTO in/out) |
| `ReflectionUseCase` | `brain.application.usecases.reflection` | `ReflectionMaintenanceService` | Reflection orchestration (DTO in/out) |
| `EvolutionUseCase` | `brain.application.usecases.evolution` | `ReflectionEvolutionBridge` | Evolution orchestration (DTO in/out) |
| `PlanningEngine` | `brain.planning.planner` | `PlanningUseCase` | Pure planning capability |
| `ReflectionEngine` | `brain.reflection.engine` | `ReflectionUseCase` | Pure reflection capability |
| `EvolutionPlanner` | `brain.evolution.planning` | `EvolutionUseCase` | Pure evolution planning |
| `EvolutionExecutor` | `brain.evolution.executor` | `EvolutionUseCase` | Plan execution |
| `EvolutionEngine` | `brain.evolution.evolution` | `EvolutionUseCase` | Conflict recording, transition history |
| `ExecutionEngine` | `brain.execution.executor` | `ExecutionUseCase` | Plan execution |
| `LearningCoordinator` | `brain.learning.coordinator` | `LearningUseCase` | Learning coordination |
| `KnowledgeRepository` | `brain.repositories.base` | UseCases, Engines | Persistence contract |
| `EvolutionRepository` | `brain.repositories.evolution_base` | `EvolutionUseCase`, `EvolutionExecutor` | Evolution persistence contract |
| `EvolutionUnitOfWork` | `brain.application.usecases.unit_of_work` | `EvolutionUseCase` only | Transaction boundary contract |
| `BrainWorkflow` | `brain.application.workflow.workflow` | `Runtime`, `Adapter` | Workflow coordination |
| `BrainSession` | `brain.application.brain_session` | `BrainWorkflow`, `Adapter` | Session lifecycle |

**Composition Root Exception:** `brain.runtime.factory` is the composition root and may import concrete implementations (`SQLiteKnowledgeRepository`, `InMemoryKnowledgeRepository`, `BrainAdapter`, `BrainWorkflow`, `SequentialStrategy`, etc.) for dependency wiring only. It contains no business logic.

---

## Circular Dependency Rules

The Hermes architecture must remain a Directed Acyclic Graph (DAG). Dependencies must flow strictly:

```
Runtime (Composition Root)
    ▼
Application (Workflow, UseCases)
    ▼
Cognitive Engines (Planning, Reflection, Evolution, Execution, Learning, ...)
    ▼
Domain (Pure data models)
    ▼
Infrastructure (Repositories, Events, Pipeline, SQLite)
```

### Rules

1. **No cycles in import graph** — The full `brain.*` module graph must be acyclic (no A→B→C→A).

2. **No downward dependencies** — A layer must not import from a layer ABOVE it in the hierarchy.

3. **Domain purity** — `brain.domain` imports only stdlib and itself. No other `brain.*` imports.

4. **Infrastructure isolation** — Infrastructure (`repositories`, `events`, `pipeline`, `sqlite`) imports only `domain` and `stdlib`. Not engines, application, or runtime.

5. **Engine isolation** — Engines (`planning`, `reflection`, `evolution`, `execution`, `learning`, `validation`, `detection`, `retrieval`, `services`) import only `domain`, `infrastructure`, and other engines. Never `application`, `runtime`, `adapter`.

6. **Application layer** — Application (`workflow`, `usecases`, `bridges`, `session`, `service`) imports engines, domain, adapter DTOs. Never `runtime`, `infrastructure.sqlite`, or concrete implementations.

7. **Runtime is composition root only** — `brain.runtime` may import anything for wiring. Nothing outside `adapter` and `runtime` may import `runtime`.

8. **Adapter boundary** — Adapter imports `application` (contracts), `domain`, `stdlib`, and itself. Not engines, runtime, or infrastructure implementations.

### Approved Exceptions

| Pattern | Example | Reason |
|---------|---------|--------|
| Composition Root | `RuntimeFactory` imports concrete repos, adapters, strategies | Required for dependency wiring; contains no business logic |
| Dependency Inversion | Domain Port → implemented by Application/Infrastructure | Port owned by lower layer, implemented by higher layer |
| DTO Import | Workflow imports `adapter.models` (DTOs) | DTOs are boundary contracts, not implementation |

### Enforcement

- `tests/architecture/test_circular_dependencies.py` — 9 tests verifying all rules
- `tests/architecture/test_public_api_contract.py` — 40 tests verifying contract boundaries
- `tests/architecture/test_architectural_resilience.py` — 36 tests verifying invariants under stress
- Run: `python -m pytest tests/architecture/ -v`

---

## Architectural Invariants

**Architectural laws** describe how Hermes is built (structure).

**Architectural invariants** describe what must remain true under all circumstances, including failures (resilience).

These invariants are permanent guarantees. They are not best practices — they are architectural contracts that must hold even when execution fails.

### Category A — Layer Invariants

| ID | Invariant | Description | Stress Scenario |
|----|-----------|-------------|-----------------|
| I-1 | Planning remains pure | Planning must never mutate repositories, own transactions, or perform persistence — even if planning fails | Planning failure injection |
| I-2 | Execution never replans | Execution consumes plans. Execution never creates plans. Even during failures. | Execution failure injection |
| I-3 | Reflection remains observational | Reflection may report findings. Reflection never mutates knowledge. Reflection never executes evolution. | Reflection crash injection |
| I-4 | Evolution executes approved plans only | Execution never invents strategies. Execution never modifies plans. | Evolution execution abort |
| I-5 | Workflow coordinates only | Workflow never performs cognitive reasoning. | Workflow interruption |

### Category B — State Invariants

| ID | Invariant | Description | Stress Scenario |
|----|-----------|-------------|-----------------|
| I-6 | Every mutable state has exactly one owner | Failures must not duplicate ownership | Failure + rollback |
| I-7 | Session state never leaks | Repeated failures must not contaminate future sessions | Repeated retry |
| I-8 | Rollback removes partial ownership | After rollback: no orphan state, no duplicate state, no partial state | Transaction abort |
| I-9 | Failed operations never create persistent artifacts | Failed ops leave zero persistent footprint | Failed evolution execution |

### Category C — Contract Invariants

| ID | Invariant | Description | Stress Scenario |
|----|-----------|-------------|-----------------|
| I-10 | Public APIs expose DTOs only | External boundaries receive/send DTOs, never internal domain objects | Invalid DTO submission |
| I-11 | Internal domain objects never escape application boundaries | Domain objects (Plan, Goal, KnowledgeVersion, EvolutionPlan) never cross application boundary | Boundary crossing attempt |
| I-12 | Dependency inversion remains intact | Ports remain stable. Implementations remain replaceable. | Implementation swap |

### Category D — Failure Invariants

| ID | Invariant | Description | Stress Scenario |
|----|-----------|-------------|-----------------|
| I-13 | Failures remain localized | Failure in one subsystem must not violate another subsystem | Subscriber failure injection |
| I-14 | Every failure has one owner | Recovery responsibility must remain unambiguous | Failure propagation test |
| I-15 | Recovery never violates architecture | Rollback must never require planning. Planning must never perform recovery. Repositories must never perform reasoning. | Rollback under failure |

### Category E — Evolution Invariants

| ID | Invariant | Description | Stress Scenario |
|----|-----------|-------------|-----------------|
| I-16 | Evolution never bypasses planners | All evolution goes through EvolutionPlanner | Direct evolution attempt |
| I-17 | Evolution execution remains deterministic | Same plan + same state = same result | Repeated evolution execution |
| I-18 | Evolution preserves architectural laws | Evolution must never weaken Hermes architecture | Evolution under failure |

### Resilience Philosophy

Hermes architecture is not resilient by accident. It is resilient by **invariant design**:

1. **Fault isolation by layer** — Failures cannot propagate upward (application → engine) or sideways (engine → engine).
2. **Deterministic recovery** — Rollback, rollforward, retry all produce architecturally valid states.
3. **Invariant-first testing** — Every resilience test documents which invariant it verifies.
4. **No best-effort guarantees** — Invariants hold *always*, not "usually" or "under load".

### Relationship: Laws ↔ Invariants

| Law (Structure) | Invariant (Resilience) |
|-----------------|------------------------|
| Law 1: Engines don't depend on Application | I-1, I-2, I-3, I-4, I-5: Engine purity survives failures |
| Law 4: Planning is pure | I-1: Purity survives planning failures |
| Law 5: Planner creates intent only | I-4: Evolution never bypasses planner |
| Law 6: Executor executes only | I-2: Execution never replans |
| Law 7: UseCase owns transactions | I-8, I-9: Rollback removes artifacts, no partial state |
| Law 8: Repository owns primitives | I-6, I-7: State ownership preserved under failure |
| Law 10: No boundary bypass | I-10, I-11, I-12: Contracts survive invalid inputs |

---

## Current Status

- **Test count:** 1472 passing (full suite)
- **Architecture tests:** 215 (40 contract + 9 circular + 36 resilience + 58 controlled failure simulation + 72 other)
- **Current phase:** Milestone 25 Stabilization
- **Active task:** Stabilization Part A.8 — Controlled Architecture Failure Simulation Complete

---

## Controlled Architecture Failure Simulation (A.8)

### Purpose

A.8 verifies that Hermes handles complex failure chains and recovery paths according to its architectural rules. The goal is not to prove Hermes always recovers — it is to prove **every failure has exactly one recovery owner, recovery follows architectural rules, and architecture invariants hold under multi-layer failures.**

### Recovery Ownership

Every failure maps to exactly one UseCase as its recovery owner:

| Failure Origin | Recovery Owner | Escalation Path |
|----------------|----------------|-----------------|
| PlanningEngine | PlanningUseCase | Component → UseCase |
| ExecutionEngine | ExecutionUseCase | Component → UseCase |
| LearningCoordinator | LearningUseCase | Component → UseCase |
| ReflectionEngine | ReflectionUseCase | Component → UseCase |
| EvolutionPlanner/Executor | EvolutionUseCase | Component → UseCase |
| Repository (transient) | EvolutionUseCase | Component → UseCase |

**Recovery must never belong to:**
- **Workflow** (`BrainWorkflow`) — orchestrates only, no recovery logic
- **Engines** (PlanningEngine, ExecutionEngine, ReflectionEngine, EvolutionPlanner, EvolutionExecutor) — pure cognitive components
- **Repositories** (KnowledgeRepository, EvolutionRepository) — persistence primitives only
- **Bridges** (ReflectionEvolutionBridge, ExecutionLearningMapper) — DTO translation only

### Failure Classification

**Recoverable Failures** (controlled recovery expected):
- Temporary repository failure (transient I/O)
- Learning failure (validation rejected, publisher unavailable)
- Reflection failure (detector crashed)
- Execution interruption (handler error, policy stop)

**Non-Recoverable Failures** (reject and stop safely):
- Corrupted plans (structural invalidity)
- Invalid contracts (DTO boundary violations)
- Architectural violations (bypass planner, mutate architecture, violate ownership)

### Escalation Rules

Failures escalate through defined boundaries:
1. **Component level** — Engine/Repository raises domain exception
2. **UseCase level** — UseCase catches, translates to DTO result, owns rollback if needed
3. **Workflow level** — Workflow captures exception, returns failure report (no crash)
4. **Architectural violation level** — Hard stop, no partial state

### A.8 Verification Scope

The test suite `tests/architecture/test_controlled_failure_simulation.py` covers:

| Test Suite | Scenarios | Verifies |
|------------|-----------|----------|
| `TestCascadingFailures` | 6 | Planning→Execution→Learning→Reflection→Evolution failure chains contained |
| `TestRecoveryOwnership` | 8 | Single owner per failure, no duplicate/hidden recovery |
| `TestIllegalRecoveryAttempts` | 6 | Workflow replanning, Reflection evolution, Repository reasoning, Executor planning, DTO violations, Transaction boundary violations all rejected |
| `TestFailureEscalation` | 7 | Correct escalation: Component→UseCase→Workflow→Report |
| `TestArchitectureDamageVerification` | 10 | Post-failure: dependencies, responsibilities, state ownership, contracts, transactions, invariants all intact |
| `TestFailureClassification` | 5 | Recoverable vs non-recoverable handled correctly |
| `TestFailureSimulationMatrix` | 1 | Complete failure→owner→escalation→invariant→result documentation |
| `TestRecoveryOwnershipVerification` | 3 | All failures mapped to verified UseCase owners |
| `TestArchitecturePreservationEvidence` | 5 | No responsibility leakage, state corruption, contract violations, dependency violations, transaction violations |
| `TestFinalAssessment` | 1 | Final YES/NO: Architecture preserved? |

**Total: 58 tests**

### Key Results

All 58 A.8 tests pass, confirming:

- ✅ Every failure has exactly one recovery owner (a UseCase)
- ✅ No illegal recovery: Workflow never replans, Reflection never evolves, Repositories never reason, Engines never own transactions
- ✅ Failures escalate correctly through architectural boundaries
- ✅ After every failure simulation: all 6 architecture dimensions preserved (dependencies, responsibilities, state ownership, contracts, transactions, invariants)
- ✅ Recoverable failures → controlled recovery; Non-recoverable → reject and stop safely
- ✅ No responsibility leakage, state corruption, contract violations, dependency violations, or transaction violations

**A.8 Assessment: YES — Hermes preserves its constitutional architecture during controlled multi-layer failures.**

---

## Future Rules

Before implementing any future milestone:

1. Read this document.
2. Preserve architectural laws.
3. Avoid introducing new layers without justification.
4. Prefer small incremental changes.
5. Update this document if architecture genuinely changes.

---

# Phase B — Controlled Self-Evolution Architecture

## Evolution Constitution (B.0 Foundation)

The Evolution Constitution establishes the conceptual foundation for controlled self-evolution. It defines the immutable separation between observation, proposal, evaluation, approval, and execution.

### Constitutional Principles

| Principle | Statement |
|-----------|-----------|
| **Observation ≠ Proposal** | A finding is a discovered opportunity, not a solution. |
| **Proposal ≠ Execution** | A proposal is a suggested improvement, not a mutation command. |
| **Evaluation precedes mutation** | No change occurs without explicit evaluation of benefit, risk, and architectural impact. |
| **Evolution history is preserved** | Every attempt (approved or rejected) creates a permanent audit record. |
| **Constitutional laws cannot be changed by normal evolution** | The constitutional laws in this document are fixed. Changing them requires explicit architectural review, not self-evolution. |

### Domain Models (B.0)

The following pure domain models represent the evolution constitution. They reside in `brain/domain/evolution.py` and have **zero dependencies** on application, runtime, adapters, repositories, infrastructure, or engines.

| Model | Purpose | Contains | Does NOT Contain |
|-------|---------|----------|------------------|
| `EvolutionFinding` | Discovered improvement opportunity | category, target, evidence, description, confidence, detection metadata | solution, execution instructions, mutation commands |
| `EvolutionProposal` | Suggested improvement for a finding | target, proposed change, expected benefit, risk level/description, prerequisites | execution logic, mutation commands |
| `EvolutionEvaluation` | Analysis of proposal merit and impact | benefit/risk/architecture/constitutional assessment, confidence, notes | decision, execution logic |
| `EvolutionDecision` | Governance outcome | state (APPROVED/REJECTED/REQUIRES_REVIEW), rationale, decider, conditions | execution logic |
| `EvolutionRecord` | Permanent evolution history | finding, proposal, evaluation, decision, timestamps, execution placeholder | execution results (separate) |

### Enums (B.0)

| Enum | Values | Purpose |
|------|--------|---------|
| `EvolutionCategory` | ARCHITECTURAL, PERFORMANCE, CORRECTNESS, MAINTAINABILITY, SECURITY, STRATEGIC, OPERATIONAL | Classify findings |
| `ProposalRiskLevel` | NEGLIGIBLE, LOW, MEDIUM, HIGH, CRITICAL | Risk assessment for proposals |
| `DecisionState` | APPROVED, REJECTED, REQUIRES_REVIEW | Governance decision outcomes |

### Evolution Constitution Laws (New)

| Law | Statement |
|-----|-----------|
| **EC-1** | Every evolution begins with a Finding (observation), not a Proposal. |
| **EC-2** | Every Proposal must reference a Finding. |
| **EC-3** | Every Decision must reference an Evaluation. |
| **EC-4** | Every Evaluation must assess: benefit, risk, architecture impact, constitutional compliance. |
| **EC-5** | EvolutionRecord captures the complete lifecycle: Finding → Proposal → Evaluation → Decision. |
| **EC-6** | Constitutional laws (DL-1 through DL-8, RL-1 through RL-7, SL-1 through SL-8, CL-1 through CL-5, EL-1 through EL-6, EC-1 through EC-6) cannot be modified by normal evolution. |
| **EC-7** | Approved evolutions execute through the existing EvolutionExecutor (transactional, via EvolutionUseCase). |
| **EC-8** | Rejected evolutions create no artifacts and leave no partial state. |
| **EC-9** | Quarantined targets (from EvolutionContext) are excluded from normal evolution planning. |
| **EC-10** | All evolution attempts (approved, rejected, pending) create permanent audit records. |

### Separation Guarantees

| Separation | Enforced By |
|------------|-------------|
| Finding ≠ Proposal | Different domain classes; Finding has no proposed_change |
| Proposal ≠ Execution | Proposal is passive data; execution is EvolutionExecutor |
| Evaluation ≠ Decision | Evaluation provides analysis; Decision records governance outcome |
| History ≠ Execution | EvolutionRecord is historical; EvolutionExecutor produces ExecutionFailureRecord |
| Constitution ≠ Evolution | Constitutional laws are fixed; evolution operates within them |

### B.0 Test Coverage

Domain-level tests in `tests/architecture/` verify:

- Evolution models remain in domain layer (no forbidden imports)
- Finding/Proposal/Evaluation/Decision separation is explicit
- Decision states are exhaustive and explicit
- EvolutionRecord preserves complete lifecycle
- Zero dependencies on application, runtime, adapters, repositories, infrastructure, or engines

**B.0 Implementation: COMPLETE — Evolution Constitution foundation established.**

---

## Self Observation Architecture (B.1)

### Purpose

B.1 introduces the first capability required for controlled evolution: **Self Observation**.

> **Self Observation** = Hermes can represent observations about its own internal state.
>
> It answers: *"What is happening inside me?"*
>
> It does NOT answer: *"What should I change?"*

### Constitutional Principles

| Principle | Statement |
|-----------|-----------|
| **Observation ≠ Proposal** | A finding is a discovered signal, not a solution. |
| **Observation ≠ Evaluation** | Evidence supports observation; it does not interpret meaning. |
| **Observation ≠ Decision** | Observations contain no recommendations, decisions, or solutions. |
| **Observation ≠ Mutation** | Observation objects describe state; they never mutate components. |

### Self Observation Laws (New)

| Law | Statement |
|-----|-----------|
| **O-1** | Observation describes facts only. No recommendations, decisions, or solutions. |
| **O-2** | Observation contains no decisions. No `should_change`, `recommended_action`, `solution`. |
| **O-3** | Observation contains no decisions. No `decision`, `proposal`, `evaluation`. |
| **O-4** | Observation cannot mutate observed systems. No `create`, `update`, `execute`, `run` methods. |
| **O-5** | Evidence and interpretation remain separate. ObservationEvidence supports; it does not interpret. |
| **O-6** | Observation does not create EvolutionProposal objects. Separation enforced by architecture tests. |

### Domain Models (B.1)

All models reside in `brain/domain/observation/` — pure domain layer with **zero dependencies** on application, runtime, adapters, repositories, infrastructure, or engines.

| Model | Purpose | Contains | Does NOT Contain |
|-------|---------|----------|------------------|
| `ObservationSignal` | One measured fact | category, source, metric_name, value, unit, timestamp | recommendations, decisions, solutions |
| `ObservationEvidence` | Why observation exists | description, sample_count, measurement_period, confidence, metadata | interpretation, diagnosis, severity assignment |
| `SystemObservation` | One self-observation | target, category, signal, evidence, confidence, timestamp | should_change, recommended_action, solution, decision |
| `ObservationSnapshot` | State at a point in time | timestamp, collection_id, observations | comparison, trends, proposals |

### Observation Categories

| Category | Description |
|----------|-------------|
| `OPERATIONAL` | Execution metrics, failure rates, latency, throughput |
| `COGNITIVE` | Planning depth, reflection finding counts, learning acceptance rates |
| `EVOLUTION_HISTORY` | Evolution attempt counts, approval/rejection ratios, quarantine status |

**Categories describe ORIGIN only** — not severity, urgency, or required action.

### Separation Guarantees

| Separation | Enforced By |
|------------|-------------|
| `SystemObservation` ≠ `EvolutionProposal` | Different modules; no cross-imports; architecture tests |
| `SystemObservation` ≠ `ReflectionFinding` | Different modules; no cross-imports; architecture tests |
| `ObservationEvidence` ≠ Interpretation | No `interpret`, `diagnose`, `analyze`, `recommend` methods; tests verify |
| `ObservationSnapshot` ≠ Analysis | No `compare`, `trend`, `detect`, `calculate` methods; tests verify |

### B.1 Test Coverage

Architecture tests in `tests/architecture/test_observation_architecture.py` verify:

- Domain purity: 0 forbidden imports (O-1)
- Read-only design: 0 mutation methods (O-2, O-3, O-4)
- Evidence/interpretation separation: 0 interpretation methods (O-5)
- Evolution separation: 0 EvolutionProposal references (O-6)
- Reflection separation: 0 reflection imports
- Category constraints: no action-oriented category names
- Snapshot constraints: no analysis methods

**Total: 10 new architecture tests — ALL PASS**

**B.1 Implementation: COMPLETE — Self Observation foundation established.**

---

## Phase B Milestones (Planned)

| Milestone | Scope | Status |
|-----------|-------|--------|
| **B.0** | Evolution Constitution Foundation | ✅ COMPLETE |
| **B.1** | Self Observation — detecting evolution opportunities | ⏳ PLANNED |
| **B.2** | Proposal Generation — creating improvement proposals | ⏳ PLANNED |
| **B.3** | Evaluation & Decision — analyzing and approving proposals | ⏳ PLANNED |
| **B.4** | Execution & Verification — running approved evolutions | ⏳ PLANNED |
| **B.5** | Constitutional Amendment Process — changing constitutional laws | ⏳ PLANNED |
