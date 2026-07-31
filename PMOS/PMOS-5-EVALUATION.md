# PMOS-5: Evaluation Engine

## Purpose
Analyze proposals analytically — strengths, weaknesses, tradeoffs, evidence. The Evaluation Engine provides structured reasoning without making decisions.

---

## Constitutional Contract

### Consumes
- `ProposalSpace` (from Proposal Engine)
- `ProblemStatement` (from Problem Engine)
- Active evaluation policies

### Produces
- `Evaluation` — analytical assessment of one Proposal
- `EvaluationSpace` — collection of evaluations

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Hypothesis generation
- ❌ Problem formulation
- ❌ Proposal generation
- ❌ Governance
- ❌ Authorization
- ❌ Execution
- ❌ Ranking, scoring, or prioritizing proposals
- ❌ Decision making
- ❌ Proposal selection
- ❌ Proposal optimization

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `ProposalSpace` | `brain.domain.proposal` | Proposals to evaluate |
| `ProblemStatement` | `brain.domain.problem` | Context for evaluation |
| `EvaluationPolicy` | `brain.domain.evaluation` | Evaluation rules |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `Evaluation` | `brain.domain.evaluation` | Analytical assessment |
| `EvaluationSpace` | `brain.domain.evaluation` | Collection of evaluations |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| E-1: Evaluation ≠ Proposal | No imports from `brain.domain.proposal` logic |
| E-2: Evaluation ≠ Decision | No `DecisionState`, no `approved/rejected/accepted` fields |
| E-3: Evaluation ≠ Execution | No `ExecutionPlan`, `ExecutionResult` imports |
| E-4: No Proposal mutation | No `proposal_id:` setters, no mutation methods |
| E-5: No Proposal creation | No `create_proposal`, `generate_proposal` methods |
| E-6: Uncertainty preserved | No `score:`, `confidence:`, `ranking:`, `priority:`, `severity:`, `probability:`, `usefulness:` fields |
| E-7: Explicit evidence | `evidence_ids`, `DimensionalAnalysis.evidence` |
| E-8: Explicit tradeoffs | `Tradeoff` model, `global_tradeoffs`, `tradeoff_ids` |
| E-9: Never ranks | No `rank`, `sort`, `filter`, `select`, `choose`, `pick`, `best`, `evaluate`, `score`, `compare`, `judge`, `prefer`, `merge`, `optimize`, `reduce`, `eliminate` methods |
| E-10: Never filters | `EvaluationSpace` preserves all evaluations |
| E-11: Never approves | No `approved:`, `rejected:`, `accepted:` fields |
| E-12: Deterministic | All models `frozen=True`; same inputs = same outputs |
| E-13: Comparison ≠ Ranking | `evaluations_by_proposal` for comparison; no ranking |
| E-14: Independent evaluation | Each `Evaluation` has `proposal_id`; `EvaluationSpace` preserves all |
| E-15: Immutable history | `superseded_by` field; frozen dataclasses |
| E-16: Explainable through evidence | `summary_judgment`, `known_uncertainties`, explicit `evidence_ids` |

---

## Input/Output Specification

### Input: EvaluationRequest
```python
@dataclass(frozen=True)
class EvaluationRequest:
    proposal_id: UUID
    proposal_space_id: UUID
    problem_statement_id: UUID
    policy: EvaluationPolicy
    context: Tuple[str, ...] = ()
```

### Output: EvaluationSpace
```python
@dataclass(frozen=True)
class EvaluationSpace:
    space_id: UUID
    problem_statement_id: UUID
    proposal_ids: Tuple[UUID, ...]
    evaluations: Tuple[Evaluation, ...]
    created_at: datetime
```

### Output: Evaluation
```python
@dataclass(frozen=True)
class Evaluation:
    evaluation_id: UUID
    proposal_id: UUID
    state: str = "draft"  # EvaluationState value as string
    
    # Structured reasoning
    dimensional_analyses: Tuple[DimensionalAnalysis, ...] = ()
    global_tradeoffs: Tuple[Tradeoff, ...] = ()
    evidence_ids: Tuple[UUID, ...] = ()
    
    # Summary reasoning (qualitative, not decision)
    summary_judgment: str = ""
    known_uncertainties: Tuple[str, ...] = ()
    
    created_at: datetime
    superseded_by: Optional[UUID] = None  # E-15
    
    def __post_init__(self) -> None:
        pass  # No validation required

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None
```

### Supporting Models
```python
@dataclass(frozen=True)
class DimensionalAnalysis:
    analysis_id: UUID
    dimension: EvaluationDimension
    facts: Tuple[str, ...] = ()
    judgments: Tuple[str, ...] = ()
    evidence: Tuple[UUID, ...] = ()
    tradeoff_ids: Tuple[UUID, ...] = ()
    created_at: datetime

@dataclass(frozen=True)
class Tradeoff:
    tradeoff_id: UUID
    benefit: str
    cost: str
    dimension: str
    created_at: datetime

@dataclass(frozen=True)
class EvaluationEvidence:
    evidence_id: UUID
    evidence_type: EvidenceType
    description: str
    observation_ids: Tuple[UUID, ...] = ()
    hypothesis_ids: Tuple[UUID, ...] = ()
    problem_ids: Tuple[UUID, ...] = ()
    proposal_ids: Tuple[UUID, ...] = ()
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

---

## Engine Interface

```python
class EvaluationEngine:
    """
    Constitutional contract: Pure analytical function of ProposalSpace → EvaluationSpace.
    No state. No side effects. No ranking. No decisions.
    """
    
    def evaluate(
        self,
        request: EvaluationRequest
    ) -> Evaluation:
        """
        Produce a complete analytical evaluation of a single proposal.
        
        Must produce Evaluation with:
        - DimensionalAnalyses covering relevant EvaluationDimensions
        - Explicit Tradeoffs with benefit/cost/dimension
        - EvidenceIDs tracing to Observations/Hypotheses/Problems/Proposals
        - SummaryJudgment (qualitative, not decision)
        - KnownUncertainties (explicit acknowledgment of limits)
        
        Must NOT contain:
        - score, confidence, ranking, priority, severity, probability, usefulness
        - approved, rejected, accepted, rejected
        - decision, decision_id, governance, execution_plan
        - mutation methods, execution methods
        
        Raises:
            InsufficientEvidenceError: Insufficient evidence for evaluation
            PolicyViolationError: Request violates evaluation policy
        """
        ...
    
    def evaluate_space(
        self,
        space: EvaluationRequest
    ) -> EvaluationSpace:
        """Evaluate all proposals in a space independently."""
        ...
    
    def compare_evaluations(
        self,
        space: EvaluationSpace,
        dimension: EvaluationDimension
    ) -> Dict[UUID, DimensionalAnalysis]:
        """
        Compare evaluations across proposals along a single dimension.
        
        Returns mapping of proposal_id → DimensionalAnalysis.
        Does NOT rank, sort, select, or judge.
        """
        ...
    
    def supersede(
        self,
        evaluation_id: UUID,
        new_evaluation: Evaluation
    ) -> Evaluation:
        """Create a superseded evaluation (immutable history)."""
        ...
```

---

## Quality Gates

### Evaluation Validation
- ✅ No `score:`, `confidence:`, `ranking:`, `priority:`, `severity:`, `probability:`, `usefulness:` fields
- ✅ No `approved:`, `rejected:`, `accepted:`, `rejected:` fields
- ✅ No `decision:`, `decision_id:`, `governance:`, `execution_plan:` fields
- ✅ No `mutation:`, `execute:`, `run:`, `apply:` methods
- ✅ `dimensional_analyses` as tuple of `DimensionalAnalysis`
- ✅ `global_tradeoffs` as tuple of `Tradeoff`
- ✅ `evidence_ids` trace to Observation/Hypothesis/Problem/Proposal
- ✅ `summary_judgment` is qualitative, not decision
- ✅ `known_uncertainties` explicitly declared

### Space Validation
- ✅ `evaluations_by_proposal()` for comparison
- ✅ No `rank`, `sort`, `filter`, `select`, `choose`, `pick`, `best`, `evaluate`, `score`, `compare`, `judge`, `prefer`, `merge`, `optimize`, `reduce`, `eliminate` methods
- ✅ All evaluations preserved (no filtering/elimination)

### Constitutional Compliance
- ✅ No Proposal imports in logic
- ✅ No Decision imports
- ✅ No Execution imports
- ✅ No Governance imports
- ✅ No Execution imports
- ✅ All models `frozen=True`
- ✅ Same inputs → same outputs (deterministic)

---

## Dependencies

### Allowed
- `brain.domain.evaluation` (Evaluation, EvaluationSpace, DimensionalAnalysis, Tradeoff, EvaluationEvidence, EvaluationDimension, EvidenceType, EvaluationState)
- `brain.domain.proposal` (ProposalSpace, Proposal - identifiers only)
- `brain.domain.problem` (ProblemStatement)
- `brain.domain.observation` (SystemObservation)
- `brain.domain.hypothesis` (HypothesisSpace)
- `brain.domain.references` (Evidence, Relationship)
- Standard library only

### Forbidden
- `brain.application.*`
- `brain.runtime.*`
- `brain.adapter.*`
- `brain.repositories.*`
- `brain.infrastructure.*`
- `brain.planning.*`
- `brain.reflection.*`
- `brain.evolution.*`
- `brain.learning.*`
- `brain.execution.*`
- `brain.validation.*`
- `brain.detection.*`
- `brain.retrieval.*`
- `brain.services.*`
- `brain.governance.*`
- `brain.authorization.*`
- `brain.authorization.*`
- `brain.execution.*`
- Any engine module