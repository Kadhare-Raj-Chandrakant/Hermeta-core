# Hermes Engine Contracts

This document specifies the constitutional contract for every engine in Hermes.
Engines are pure domain components — they must never violate their boundaries.

---

## 1. Observation Engine

**Purpose**: Detect and record raw signals from the environment.

**Consumes**:
- Raw environmental input (stdin, files, API events, telemetry)
- Active observation policies

**Produces**:
- `ObservationSignal` (raw measured facts)
- `ObservationEvidence` (supporting metadata)

**Forbidden Responsibilities**:
- Interpretation of signals
- Hypothesis formation
- Problem identification
- Proposal generation
- Evaluation
- Governance
- Authorization
- Execution
- Storage beyond ephemeral buffering

**Dependencies Allowed**:
- `brain.domain` (ObservationSignal, ObservationEvidence, SignalCategory)
- `brain.domain.observation` (ObservationSignal, ObservationEvidence, SystemObservation)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any engine module

---

## 2. Hypothesis Engine

**Purpose**: Generate competing explanations for observed facts.

**Consumes**:
- `SystemObservation` (from Observation Engine)
- `ObservationEvidence`
- Active hypothesis policies

**Produces**:
- `Hypothesis` (competing explanations)
- `HypothesisSpace` (collection of competing hypotheses)

**Forbidden Responsibilities**:
- Observation collection
- Problem formulation
- Proposal generation
- Evaluation
- Governance
- Authorization
- Execution
- Ranking or selection of hypotheses

**Dependencies Allowed**:
- `brain.domain` (Hypothesis, HypothesisSpace, HypothesisCategory)
- `brain.domain.observation` (SystemObservation, ObservationEvidence)
- `brain.domain.problem` (ProblemCategory)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any other engine module

---

## 3. Problem Engine

**Purpose**: Formulate structured cognitive gaps from competing hypotheses.

**Consumes**:
- `HypothesisSpace` (from Hypothesis Engine)
- Active problem formulation policies

**Produces**:
- `ProblemStatement` (structured cognitive gap)
- `ProblemSpace` (related problems)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Proposal generation
- Evaluation
- Governance
- Authorization
- Execution
- Solution generation

**Dependencies Allowed**:
- `brain.domain` (ProblemStatement, ProblemSpace, ProblemCategory, ProblemSeverity)
- `brain.domain.hypothesis` (Hypothesis, HypothesisSpace)
- `brain.domain.problem` (ProblemStatement, ProblemSpace)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any other engine module

---

## 4. Proposal Engine

**Purpose**: Generate candidate improvements for formulated problems.

**Consumes**:
- `ProblemStatement` (from Problem Engine)
- `ProblemSpace`
- Active proposal policies

**Produces**:
- `Proposal` (candidate improvements)
- `ProposalSpace` (alternative proposals)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Problem formulation
- Evaluation
- Governance
- Authorization
- Execution
- Ranking or selection of proposals

**Dependencies Allowed**:
- `brain.domain` (Proposal, ProposalSpace, ProposalCategory, ProposalAssumption, ProposalOutcome)
- `brain.domain.problem` (ProblemStatement, ProblemSpace)
- `brain.domain.proposal` (Proposal, ProposalSpace)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any other engine module

---

## 5. Evaluation Engine

**Purpose**: Analyze proposals analytically — strengths, weaknesses, tradeoffs, evidence.

**Consumes**:
- `ProposalSpace` (from Proposal Engine)
- `ProblemStatement` (from Problem Engine)
- Active evaluation policies

**Produces**:
- `Evaluation` (analytical assessment)
- `EvaluationSpace` (collection of evaluations)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Problem formulation
- Proposal generation
- Governance
- Authorization
- Execution
- Ranking, scoring, or ranking proposals
- Decision making
- Proposal optimization

**Dependencies Allowed**:
- `brain.domain` (Evaluation, EvaluationSpace, EvaluationDimension, Tradeoff, EvaluationEvidence, DimensionalAnalysis)
- `brain.domain.proposal` (Proposal, ProposalSpace)
- `brain.domain.problem` (ProblemStatement, ProblemSpace)
- `brain.domain.hypothesis` (HypothesisSpace)
- `brain.domain.observation` (SystemObservation)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any governance, authorization, or execution module

---

## 6. Governance Engine

**Purpose**: Determine constitutional permissibility of evaluated proposals.

**Consumes**:
- `EvaluationSpace` (from Evaluation Engine)
- Active constitutional policies

**Produces**:
- `GovernanceDecision` (constitutional outcome)
- `GovernanceRationale` (constitutional justification)
- `GovernanceFinding` (constitutional observations)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Problem formulation
- Proposal generation
- Evaluation
- Authorization
- Execution
- Optimization
- Retry logic
- Recovery reasoning

**Dependencies Allowed**:
- `brain.domain` (GovernanceDecision, DecisionContext, GovernanceHistory, GovernancePolicy, GovernanceRationale, GovernanceFinding)
- `brain.domain.evaluation` (Evaluation, EvaluationSpace)
- `brain.domain.proposal` (ProposalSpace - identifiers only)
- `brain.domain.problem` (ProblemStatement - identifiers only)
- `brain.domain.governance` (GovernanceDecision, GovernanceRationale, GovernanceFinding, GovernancePolicy)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any authorization, execution, evaluation, or proposal module

---

## 7. Authorization Engine

**Purpose**: Grant or deny constitutional permission for a governed decision to proceed.

**Consumes**:
- `GovernanceDecision` (from Governance Engine)
- Active authorization policies

**Produces**:
- `AuthorizationRecord` (permission grant/denial)
- `AuthorizationToken` (execution artifact)
- `AuthorizationHistory` (immutable audit trail)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Problem formulation
- Proposal generation
- Evaluation
- Governance
- Execution
- Scheduling
- Retry logic
- Recovery reasoning
- Optimization

**Dependencies Allowed**:
- `brain.domain` (AuthorizationRecord, AuthorizationContext, AuthorizationHistory, AuthorizationConstraint, AuthorizationRationale, AuthorizationToken)
- `brain.domain.governance` (GovernanceDecision - identifiers only)
- `brain.domain.governance` (GovernancePolicy - identifiers only)
- `brain.domain.authorization` (AuthorizationRecord, AuthorizationContext, AuthorizationHistory, AuthorizationConstraint, AuthorizationRationale, AuthorizationToken)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any governance, evaluation, proposal, problem, hypothesis, or observation module
- Any execution module

---

## 8. Execution Engine

**Purpose**: Perform the authorized action — produce observable facts only.

**Consumes**:
- `AuthorizationToken` (from Authorization Engine)
- `ExecutionPlan` (derived from authorized decision)

**Produces**:
- `ExecutionResult` (observable facts only)
- `ExecutionReceipt` (constitutional proof)
- `ExecutionArtifact` (produced artifacts)
- `ExecutionFailure` (observed failures only)
- `ExecutionHistory` (immutable audit trail)
- `ExecutionReceipt` (constitutional proof artifact)

**Forbidden Responsibilities**:
- Observation collection
- Hypothesis generation
- Problem formulation
- Proposal generation
- Evaluation
- Governance
- Authorization
- Scheduling
- Retry logic
- Recovery reasoning
- Optimization
- Reasoning
- Interpretation
- Explanation
- Recommendation
- Decision making

**Dependencies Allowed**:
- `brain.domain` (ExecutionPlan, ExecutionContext, ExecutionResult, ExecutionReceipt, ExecutionArtifact, ExecutionFailure, ExecutionHistory, ExecutionContext)
- `brain.domain.authorization` (AuthorizationToken - identifier only)
- `brain.domain.execution` (ExecutionPlan, ExecutionContext, ExecutionResult, ExecutionReceipt, ExecutionArtifact, ExecutionFailure, ExecutionHistory, ExecutionContext)
- `brain.domain.execution` (ExecutionStatus, ArtifactType, FailureType)
- Standard library only

**Dependencies Forbidden**:
- `brain.planning`, `brain.reflection`, `brain.evolution`
- `brain.application`, `brain.runtime`, `brain.adapter`
- `brain.repositories`, `brain.infrastructure`
- Any authorization, governance, evaluation, proposal, problem, hypothesis, or observation module

---

## Engine Contract Summary Matrix

| Engine | Consumes | Produces | Forbidden |
|--------|----------|----------|-----------|
| Observation | Raw input | ObservationSignal, ObservationEvidence | Interpretation, Hypothesis, Problem, Proposal, Evaluation, Governance, Authorization, Execution |
| Hypothesis | ObservationSignal, Evidence | Hypothesis, HypothesisSpace | Observation, Problem, Proposal, Evaluation, Governance, Authorization, Execution |
| Problem | HypothesisSpace | ProblemStatement, ProblemSpace | Observation, Hypothesis, Proposal, Evaluation, Governance, Authorization, Execution |
| Proposal | ProblemStatement | Proposal, ProposalSpace | Observation, Hypothesis, Problem, Evaluation, Governance, Authorization, Execution |
| Evaluation | ProposalSpace, ProblemStatement | Evaluation, EvaluationSpace | Observation, Hypothesis, Problem, Proposal, Governance, Authorization, Execution |
| Governance | EvaluationSpace | GovernanceDecision, GovernanceRationale, GovernanceFinding | Observation, Hypothesis, Problem, Proposal, Evaluation, Authorization, Execution |
| Authorization | GovernanceDecision | AuthorizationRecord, AuthorizationToken, AuthorizationHistory | Observation, Hypothesis, Problem, Proposal, Evaluation, Governance, Execution |
| Execution | AuthorizationToken, ExecutionPlan | ExecutionResult, ExecutionReceipt, ExecutionArtifact, ExecutionFailure, ExecutionHistory | Observation, Hypothesis, Problem, Proposal, Evaluation, Governance, Authorization |

---

## Constitutional Invariant: Unidirectional Flow

```
Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
```

**No backward edges.** **No horizontal edges.** Each engine is a pure function of its inputs, producing exactly its constitutional artifact.