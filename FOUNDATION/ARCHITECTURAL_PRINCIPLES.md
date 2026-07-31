# Architectural Principles

## Core Architectural Invariants

### 1. Strict Layer Separation
The architecture enforces strict layer separation through 5 layers:
- **Domain Layer** — Pure data models, zero external dependencies
- **Engine Layer** — Pure functions implementing constitutional contracts
- **Application Layer** — Orchestration, no business logic
- **Infrastructure Layer** — Concrete implementations of domain contracts
- **Runtime Layer** — Composition root only, no business logic

### 2. Dependency Direction
Dependencies flow strictly downward:
```
Runtime → Application → Engines → Domain
```
No upward dependencies. No horizontal dependencies between engines.

### 3. Domain Purity
Domain models:
- Are `@dataclass(frozen=True)`
- Import only stdlib and other domain models
- Contain zero behavior, only data
- Never import from application, runtime, or infrastructure

### 4. Engine Contracts
Every engine has a frozen contract specifying:
- Exact inputs (domain models only)
- Exact outputs (domain models only)
- Forbidden responsibilities
- Allowed/forbidden dependencies

### 5. Immutable History
All history is append-only:
- No mutation of historical records
- Supersession creates new records
- History is immutable audit trail

### 6. Single Responsibility per Stage
Each pipeline stage has exactly one constitutional responsibility:
- Observation: Evidence collection
- Hypothesis: Explanation generation
- Problem: Gap formulation
- Proposal: Intent expression
- Evaluation: Analytical reasoning
- Governance: Constitutional adjudication
- Authorization: Permission granting
- Execution: Action performance

### 5. Traceability
Every artifact traces to originating observation through immutable ID chain.

### 6. Determinism
Same inputs → same outputs. Always. Frozen dataclasses, deterministic algorithms.

### 7. Separation of Authority and Reasoning
Decision authority (Governance) separated from reasoning (Evaluation) separated from permission (Authorization) separated from action (Execution).

### 6. Constitutional Minimality
Every field must answer: "Is this strictly required to perform an already-authorized action?"

---

## Derived Principles

### No Engine Assumptions in Domain
Domain models never contain engine-specific logic, types, or assumptions.

### No Runtime Assumptions in Domain
Domain models never assume runtime behavior, scheduling, or persistence.

### No Circular Dependencies
Verified by 420 architecture tests on every commit.

### Single Ownership
Every model has exactly one owner stage. No shared ownership.

### Constitutional Minimality
If a field doesn't serve a constitutional law, it doesn't exist.