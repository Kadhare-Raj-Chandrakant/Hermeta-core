# Constitutional Principles

## Supreme Law

The Constitution is the supreme law of Hermes. No engine, module, configuration, or runtime behavior may violate it. Amendments require explicit constitutional process.

---

## Article I — The Cognitive Pipeline

### Immutable Pipeline Order
```
Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
```
No stage may be skipped, reordered, merged, or bypassed.

### Single Responsibility
Each stage has exactly one constitutional responsibility. No stage may usurp another's constitutional role.

### Immutable Transitions
Each stage produces exactly one artifact type consumed by exactly one next stage.

---

## Article II — Separation of Concerns

| Stage | Owns | Never Does |
|-------|------|------------|
| Observation | Evidence collection | Interpretation, hypothesis, proposal |
| Hypothesis | Explanation generation | Problem formulation, proposal, evaluation |
| Problem | Gap formulation | Hypothesis, proposal, evaluation |
| Proposal | Intent expression | Evaluation, governance, execution |
| Evaluation | Analytical reasoning | Decision, governance, authorization, execution |
| Governance | Constitutional adjudication | Proposal, evaluation, authorization, execution |
| Authorization | Permission granting | Evaluation, governance, execution |
| Execution | Action performance | Reasoning, evaluation, governance, authorization |

---

## Article III — Invariants

### Immutability
All domain models are `@dataclass(frozen=True)`. History is append-only. Supersession replaces mutation.

### Determinism
Same inputs → same outputs. Always. Frozen dataclasses, deterministic algorithms, explicit seeds.

### Traceability
Every decision traces to evidence. Every artifact traces to origin. Chain unbroken.

### Uncertainty
Confidence quantified. Uncertainty documented. "I don't know" is valid, documented state.

### Traceability Chain
```
Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
```
Every link explicit, immutable, traceable.

---

## Article IV — Constitutional Supremacy

No emergency powers. No pragmatic exceptions. No temporary waivers. If the Constitution prevents necessary action, the Constitution must be amended first.