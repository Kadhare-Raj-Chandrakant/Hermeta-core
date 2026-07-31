# PMOS-4: Proposal Engine

## Purpose
Generate candidate improvements for formulated problems. The Proposal Engine expresses intent without implementation.

---

## Constitutional Contract

### Consumes
- `ProblemStatement` (from Problem Engine)
- `ProblemSpace` (from Problem Engine)
- Active proposal policies

### Produces
- `Proposal` — candidate improvement
- `ProposalSpace` — collection of alternatives

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Hypothesis generation
- ❌ Problem formulation
- ❌ Evaluation
- ❌ Governance
- ❌ Authorization
- ❌ Execution
- ❌ Ranking or selection of proposals

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `ProblemStatement` | `brain.domain.problem` | Cognitive gap to address |
| `ProblemSpace` | `brain.domain.problem` | Related problems context |
| `ProposalPolicy` | `brain.domain.proposal` | Generation rules, category rules |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `Proposal` | `brain.domain.proposal` | Candidate improvement |
| `ProposalSpace` | `brain.domain.proposal` | Alternative collection |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| P-1: Proposal ≠ Decision | No `approved`, `rejected`, `accepted`, `recommended` fields |
| P-2: Intent, not implementation | `intended_outcomes` strings; no code-level details |
| P-3: No self-evaluation | No `score`, `confidence`, `ranking`, `priority`, `severity`, `probability`, `usefulness` |
| P-4: No mutation | No `execution_plan`, `repository`, `strategy`, `mutation` fields |
| P-5: Complete traceability | `originating_problem_id`, `hypothesis_space_id`, `observation_ids` |
| P-6: Uncertainty preserved | Represents ONE possible improvement; never THE improvement |
| P-7: Space owns alternatives | `ProposalSpace` never ranks, filters, merges, optimizes |
| P-8: Creative ≠ Analytical | No evaluation logic anywhere |
| P-9: Unaware of Evaluation | No `Evaluation` imports, no `evaluation_id`, `decision_id`, `approval` fields |
| P-10: Outcome, not mechanism | `intended_outcomes` strings; no `cache`, `lru`, `index`, `algorithm`, `thread`, `lock`, `pool` |
| P-11: Categories = intent | 10 cognitive intent categories; no `CACHE`, `INDEX`, `ALGORITHM`, `LRU` |
| P-11: Immutable domain objects | All models `frozen=True` |

---

## Input/Output Specification

### Input: ProposalRequest
```python
@dataclass(frozen=True)
class ProposalRequest:
    problem_statement_id: UUID
    problem_space_id: UUID
    policy: ProposalPolicy
    context: Tuple[str, ...] = ()
```

### Output: ProposalSpace
```python
@dataclass(frozen=True)
class ProposalSpace:
    space_id: UUID
    problem_statement_id: UUID
    proposals: Tuple[Proposal, ...]
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Output: Proposal
```python
@dataclass(frozen=True)
class Proposal:
    proposal_id: UUID
    title: str
    description: str
    category: ProposalCategory
    state: ProposalState = ProposalState.GENERATED
    originating_problem_id: UUID
    hypothesis_space_id: UUID
    observation_ids: Tuple[UUID, ...] = ()
    rationale: str = ""
    assumptions: Tuple[ProposalAssumption, ...] = ()
    intended_outcomes: Tuple[str, ...] = ()
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Supporting Models
```python
@dataclass(frozen=True)
class ProposalAssumption:
    assumption_id: UUID
    description: str
    category: str
    created_at: datetime
```

---

## Engine Interface

```python
class ProposalEngine:
    """
    Constitutional contract: Pure function of problem + policy → proposal space.
    No state. No side effects. No ranking. No evaluation.
    """
    
    def generate(
        self,
        request: ProposalRequest
    ) -> ProposalSpace:
        """
        Generate candidate proposals for the given problem.
        
        Must produce ProposalSpace with:
        - Multiple proposals when policy allows
        - No ranking, scoring, or selection
        - No evaluation logic
        - Traceability to problem → hypothesis → observation
        
        Raises:
            InsufficientProblemError: Problem insufficient for proposal generation
            PolicyViolationError: Request violates proposal policy
        """
        ...
    
    def extend_space(
        self,
        space: ProposalSpace,
        additional_problem: ProblemStatement,
        policy: ProposalPolicy
    ) -> ProposalSpace:
        """Extend an existing proposal space with additional proposals."""
        ...
```

---

## Quality Gates

### Proposal Validation
- ✅ Title present and non-empty
- ✅ Description present and non-empty
- ✅ Category is valid ProposalCategory
- ✅ Rationale present and non-empty
- ✅ Intended outcomes non-empty tuple
- ✅ No `score`, `confidence`, `ranking`, `priority`, `severity`, `probability`, `usefulness` fields
- ✅ No `approved`, `rejected`, `accepted`, `recommended` fields
- ✅ No `execution_plan`, `repository`, `strategy`, `mutation` fields
- ✅ No `proposal_id`, `evaluation_id`, `decision_id`, `approval` fields

### Space Validation
- ✅ No `rank`, `sort`, `filter`, `select`, `choose`, `pick`, `best`, `evaluate`, `score`, `compare`, `judge`, `prefer`, `merge`, `optimize`, `reduce`, `eliminate` methods
- ✅ `proposals_by_category()` for deterministic access only

### Constitutional Compliance
- ✅ No evaluation logic
- ✅ No governance logic
- ✅ No authorization logic
- ✅ No execution logic
- ✅ No reasoning methods
- ✅ No interpretation methods

---

## Dependencies

### Allowed
- `brain.domain.proposal` (Proposal, ProposalSpace, ProposalCategory, ProposalState, ProposalAssumption, ProposalOutcome)
- `brain.domain.problem` (ProblemStatement, ProblemSpace)
- `brain.domain.observation` (SystemObservation)
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
- `brain.planning.*`
- `brain.reflection.*`
- `brain.evolution.*`
- `brain.learning.*`
- `brain.execution.*`
- Any engine module