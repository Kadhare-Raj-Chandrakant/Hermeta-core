# Hermes Constitutional Pipeline

This document explains the complete cognitive pipeline of Hermes — why each stage exists, why boundaries exist, and how reasoning flows through the constitutional architecture.

---

## The Complete Pipeline

```
Observation
    ↓ (evidence)
Hypothesis
    ↓ (explanation)
Problem
    ↓ (gap)
Proposal
    ↓ (intent)
Evaluation
    ↓ (analysis)
GovernanceDecision
    ↓ (authority)
AuthorizationRecord
    ↓ (permission)
AuthorizationToken
    ↓ (artifact)
Execution
    ↓ (observable fact)
ExecutionReceipt
    ↓ (future Observation)
```

This forms a **closed constitutional loop**: ExecutionReceipt becomes future Observation evidence.

---

## Stage-by-Stage Analysis

---

### 1. Observation → Hypothesis

**Why this transition exists**:
Raw signals are meaningless without explanation. Observation captures *what happened*; Hypothesis captures *why it might have happened*.

**Why Observation cannot do Hypothesis**:
- Observation captures *facts* (signals, metrics, events)
- Hypothesis captures *explanations* (causal, correlational, structural)
- Mixing them conflates evidence with interpretation
- Constitutional Law O-1: Observation contains no recommendations
- Constitutional Law H-1: Hypothesis is not a solution

**Why Hypothesis cannot do Observation**:
- Hypothesis requires observations as input
- Cannot observe what it is explaining
- Would create circular dependency (Hypothesis needs Observation, Observation cannot need Hypothesis)

---

### 2. Hypothesis → Problem

**Why this transition exists**:
Multiple competing hypotheses about the same observations reveal a cognitive gap — a *Problem*. The Problem is the structured gap that proposals must address.

**Why Hypothesis cannot do Problem**:
- Hypothesis explains *specific observations*
- Problem synthesizes *multiple hypotheses* into a structured gap
- Constitutional Law H-3: ProblemStatement may reference multiple hypotheses
- Constitutional Law H-2: Multiple hypotheses may originate from same observations
- A single hypothesis doesn't reveal the gap; the *set* of competing hypotheses does

**Why Problem cannot do Hypothesis**:
- Problem requires hypotheses as input
- Cannot generate the explanations it needs to structure
- Would create circular dependency (Problem needs Hypothesis, Hypothesis cannot need Problem)

---

### 3. Problem → Proposal

**Why this transition exists**:
A Problem defines *what is wrong*; a Proposal defines *what might fix it*. They are different cognitive acts.

**Why Problem cannot do Proposal**:
- Problem describes *what is wrong* (the gap)
- Proposal describes *what might fix it* (the intent)
- Constitutional Law H-5: Problems never contain implementation strategies
- Constitutional Law P-2: Proposal expresses intent, not implementation
- The gap and the fix are different cognitive acts

**Why Proposal cannot do Problem**:
- Proposal requires a Problem to address
- Cannot formulate the gap it is trying to fix
- Would create circular dependency (Proposal needs Problem, Problem cannot need Proposal)

---

### 4. Proposal → Evaluation

**Why this transition exists**:
A Proposal is an *idea*; Evaluation is the *analysis* of that idea. They are different cognitive modes.

**Why Proposal cannot do Evaluation**:
- Proposal is *creative* (generates alternatives)
- Evaluation is *analytical* (assesses tradeoffs)
- Constitutional Law P-7: ProposalSpace owns alternatives — never ranks, filters, evaluates
- Constitutional Law P-3: Proposal never evaluates itself
- Constitutional Law E-8: Evaluation never ranks
- Creative and analytical thinking are mutually exclusive cognitive modes

**Why Evaluation cannot do Proposal**:
- Evaluation requires proposals to evaluate
- Cannot generate the alternatives it analyzes
- Would create circular dependency (Evaluation needs Proposal, Proposal cannot need Evaluation)

---

### 5. Evaluation → Governance

**Why this transition exists**:
Evaluation provides *analysis*; Governance provides *authority*. They are different constitutional functions.

**Why Evaluation cannot do Governance**:
- Evaluation is *analytical* (assesses tradeoffs, evidence, uncertainties)
- Governance is *constitutional* (applies policy, makes binding decisions)
- Constitutional Law E-2: Evaluation ≠ Decision
- Constitutional Law E-11: Evaluation never approves
- Constitutional Law E-9: Evaluation never ranks
- Analysis and authority are different constitutional functions

**Why Governance cannot do Evaluation**:
- Governance requires Evaluation as input
- Cannot analyze what it is deciding on
- Would create circular dependency (Governance needs Evaluation, Evaluation cannot need Governance)

---

### 6. Governance → Authorization

**Why this transition exists**:
Governance provides *constitutional decision*; Authorization provides *operational permission*. They are different constitutional gates.

**Why Governance cannot do Authorization**:
- Governance decides *constitutional permissibility* (is this acceptable?)
- Authorization grants *operational permission* (may this proceed?)
- Constitutional Law G-1: Governance consumes Evaluation only
- Constitutional Law A-1: Authorization consumes GovernanceDecision only
- Constitutional Law G-4: Governance never executes
- Constitutional Law A-4: Authorization never governs
- Decision and permission are different constitutional gates

**Why Authorization cannot do Governance**:
- Authorization requires GovernanceDecision as input
- Cannot make the constitutional decision it is permitting
- Would create circular dependency (Authorization needs Governance, Governance cannot need Authorization)

---

### 7. Authorization → Execution

**Why this transition exists**:
Authorization provides *permission*; Execution provides *performance*. They are different constitutional phases.

**Why Authorization cannot do Execution**:
- Authorization grants *permission* (may this proceed?)
- Execution performs *action* (doing the authorized action)
- Constitutional Law A-5: Authorization never executes
- Constitutional Law X-5: Execution never authorizes
- Constitutional Law A-14: Authorization lifecycle independent from execution
- Permission and performance are different constitutional phases

**Why Execution cannot do Authorization**:
- Execution requires AuthorizationToken as input
- Cannot grant the permission it is performing
- Would create circular dependency (Execution needs Authorization, Authorization cannot need Execution)

---

### 8. Execution → Observation (The Feedback Loop)

**Why this transition exists**:
Execution produces observable facts (ExecutionReceipt, ExecutionResult) which become future Observation evidence. This closes the constitutional loop.

**Why Execution cannot do Observation**:
- Execution produces *facts* (what happened during authorized action)
- Observation captures *signals* (raw environmental input)
- Constitutional Law X-17: ExecutionResult becomes future Observation evidence
- Constitutional Law X-15: Execution reports observable facts only
- Execution produces the artifacts that Observation detects

**Why Observation cannot do Execution**:
- Observation captures *raw signals* from environment
- Execution performs *authorized actions* that produce facts
- They are at opposite ends of the pipeline
- The loop is closed through artifacts, not through direct dependency

---

## Why the Pipeline Must Be Linear

### No Backward Edges
Each stage consumes only from its immediate predecessor. Backward edges would create circular dependencies and violate constitutional determinism.

### No Horizontal Edges
Stages at the same "level" cannot communicate. Each stage has a single, well-defined input and output. Horizontal edges would create hidden dependencies and violate constitutional separation.

### Single Ownership
Each responsibility exists exactly once. No overlap, no ambiguity. The Responsibility Matrix ensures this.

---

## Why Each Stage Cannot Skip Its Predecessor

| Skipping | Why Impossible |
|----------|----------------|
| Hypothesis → Observation | No evidence to explain |
| Problem → Hypothesis | No explanations to structure |
| Proposal → Problem | No gap to address |
| Evaluation → Proposal | No alternatives to analyze |
| Governance → Evaluation | No analysis to base decision on |
| Authorization → Governance | No constitutional decision to permit |
| Execution → Authorization | No permission to proceed |
| Observation → Execution | No authorized action to observe |

Each stage produces the *only valid input* for the next stage. Skipping breaks constitutional traceability.

---

## Why Feedback Must Go Through Artifacts

The feedback loop (Execution → Observation) goes through **artifacts** (ExecutionReceipt), not through direct stage-to-stage communication. This preserves:

1. **Immutability** - ExecutionReceipt is immutable; future Observations cannot alter past Execution
2. **Traceability** - Every ExecutionReceipt traces back through the full chain
3. **Separation** - Execution and Observation remain separated by the artifact boundary
4. **Determinism** - Same ExecutionReceipt always produces same Observation evidence

---

## Summary: Why This Architecture Exists

| Principle | Enforced By |
|-----------|-------------|
| Every responsibility owned exactly once | Responsibility Matrix |
| No stage can do another's work | Constitutional Laws + Boundary Tests |
| No circular dependencies | DAG Dependency Direction |
| Full traceability | Immutable Traceability Chain |
| No hidden dependencies | Explicit Input/Output Contracts |
| Determinism | Frozen Dataclasses + Deterministic Pipeline |
| Constitutional minimality | Every field justified by constitutional law |

This pipeline is not arbitrary — it is the minimal constitutional structure that guarantees:
1. **Traceability** - Every execution reconstructable to its originating observation
2. **Accountability** - Every decision traces to constitutional policy
3. **Determinism** - Same inputs always produce same outputs
4. **Immutability** - History never overwritten, only superseded
5. **Separation** - No stage can usurp another's constitutional role