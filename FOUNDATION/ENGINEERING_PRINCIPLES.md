# Engineering Principles

## Core Engineering Invariants

### 1. Domain Purity
Domain layer imports only stdlib and other domain modules. Zero external dependencies.

### 2. Frozen Dataclasses
All domain models use `@dataclass(frozen=True)`. Zero mutation.

### 3. Deterministic Functions
Pure functions: same inputs → same outputs. No global state, no random seeds, no clocks.

### 3. Explicit Contracts
Every engine has a frozen contract: inputs, outputs, forbidden responsibilities, allowed/forbidden dependencies.

### 4. Explicit Traceability
Every artifact carries immutable UUID chain to originating observation.

### 5. Immutable History
History is append-only. Supersession creates new records. No mutation.

### 6. Explicit Contracts
Every public interface has a frozen contract document.

### 5. Explicit Dependencies
Dependency direction strictly enforced. Verified by 420 architecture tests.

### 6. Constitutional Minimality
Every field justifies its existence by constitutional law.

### 6. Anti-Fragility Through Constraints
Constraints create clarity. Leaky abstractions are constitutional violations.

---

## Code Quality Invariants

| Rule | Enforcement |
|------|-------------|
| No mutation | `@dataclass(frozen=True)` on all models |
| No side effects | Pure functions only in engines |
| No hidden state | No global variables, no class state |
| No implicit coupling | Explicit contracts, explicit dependencies |
| No magic | Explicit over implicit, always |
| No silent failures | Explicit errors, no silent failures |

---

## Testing Invariants

| Invariant | Test Count |
|-----------|------------|
| Domain purity | 15+ tests |
| Dependency direction | 15+ tests |
| Circular dependency freedom | 9 tests |
| Frozen dataclasses | 20+ tests |
| Traceability chain | 11 tests |
| Boundary enforcement | 15+ tests |
| Contract compliance | 420 total architecture tests |

---

## Anti-Patterns (Constitutional Violations)

| Violation | Constitutional Basis |
|-----------|---------------------|
| Domain importing engine | S-5 (Domain purity) |
| Engine mutating domain | S-5 (Immutability) |
| Engine skipping pipeline stage | Article I (Pipeline order) |
| Engine assuming runtime | S-4 (No runtime assumptions) |
| Engine mutating upstream artifact | S-5 (Immutability) |
| Domain containing behavior | S-1 (Domain purity) |
| Engine containing business logic | S-2 (Engine contracts) |
| Configuration in domain | S-1 (Domain purity) |