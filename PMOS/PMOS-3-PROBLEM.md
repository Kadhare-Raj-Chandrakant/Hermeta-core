# PMOS-3: Problem Engine

## Purpose
Formulate structured cognitive gaps from competing hypotheses. The Problem Engine bridges competing hypotheses and structured problem definitions.

---

## Constitutional Contract

### Consumes
- `HypothesisSpace` (from Hypothesis Engine)
- Active problem formulation policies

### Produces
- `ProblemStatement` — structured cognitive gap
- `ProblemSpace` — collection of related problems

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Hypothesis generation
- ❌ Proposal generation
- ❌ Evaluation
- ❌ Governance
- ❌ Authorization
- ❌ Execution
- ❌ Solution generation

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `HypothesisSpace` | `brain.domain.problem` | Competing hypotheses to structure into problems |
| `ProblemPolicy` | `brain.domain.problem` | Formulation rules, severity thresholds |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `ProblemStatement` | `brain.domain.problem` | Structured cognitive gap |
| `ProblemSpace` | `brain.domain.problem` | Collection of related problems |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| H-3: ProblemStatement references multiple hypotheses | `ProblemStatement.hypothesis_space_id` links to space |
| H-4: Observations immutable | `observation_ids` are immutable UUIDs |
| H-5: No implementation strategies | No `replace_`, `modify_`, `execute_`, `implement_` fields |
| H-6: No execution info | No `proposal_id`, `execution_plan`, `mutation`, `governance` fields |
| H-7: Independent from Proposal | No imports from `brain.domain.proposal` |

---

## Input/Output Specification

### Input: ProblemRequest
```python
@dataclass(frozen=True)
class ProblemRequest:
    hypothesis_space_id: UUID
    observations: Tuple[SystemObservation, ...]
    hypotheses: Tuple[Hypothesis, ...]
    policy: ProblemPolicy
    context: Tuple[str, ...] = ()
```

### Output: ProblemSpace
```python
@dataclass(frozen=True)
class ProblemSpace:
    space_id: UUID
    problem_ids: Tuple[UUID, ...]
    hypothesis_space_id: UUID
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Output: ProblemStatement
```python
@dataclass(frozen=True)
class ProblemStatement:
    problem_id: UUID
    title: str
    description: str
    category: ProblemCategory
    severity: ProblemSeverity
    observation_ids: Tuple[UUID, ...]
    hypothesis_space_id: Optional[UUID] = None
    affected_targets: Tuple[str, ...] = ()
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

---

## Engine Interface

```python
class ProblemEngine:
    """
    Constitutional contract: Pure function of hypotheses + policy → problem space.
    No state. No side effects. No solution generation.
    """
    
    def formulate(
        self,
        request: ProblemRequest
    ) -> ProblemSpace:
        """
        Formulate structured problems from competing hypotheses.
        
        Must produce ProblemStatement with:
        - Traceability to observations (observation_ids)
        - Traceability to hypotheses (hypothesis_space_id)
        - No solution fields
        - No implementation strategy fields
        
        Raises:
            InsufficientHypothesesError: Insufficient hypotheses for problem formulation
            PolicyViolationError: Request violates problem formulation policy
        """
        ...
    
    def relate_problems(
        self,
        space: ProblemSpace,
        new_problem: ProblemStatement
    ) -> ProblemSpace:
        """Add a new problem to an existing space."""
        ...
```

---

## Quality Gates

### Problem Validation
- ✅ Title present and non-empty
- ✅ Description present and non-empty
- ✅ Category is valid ProblemCategory
- ✅ Severity is valid ProblemSeverity
- ✅ Observation IDs non-empty
- ✅ No `solution` fields
- ✅ No `recommendation` fields
- ✅ No `implementation_plan` fields
- ✅ No `strategy` fields
- ✅ No `proposal_id` fields
- ✅ No `execution_plan` fields

### Space Validation
- ✅ At least 1 problem
- ✅ All problems reference same hypothesis_space_id
- ✅ No duplicate problem_ids

### Constitutional Compliance
- ✅ No solution fields
- ✅ No recommendation fields
- ✅ No implementation_plan fields
- ✅ No strategy fields
- ✅ No proposal_id fields
- ✅ No execution_plan fields
- ✅ No evaluation logic
- ✅ No governance logic
- ✅ No execution logic

---

## Dependencies

### Allowed
- `brain.domain.problem` (ProblemStatement, ProblemSpace, ProblemCategory, ProblemSeverity, HypothesisSpace, Hypothesis)
- `brain.domain.observation` (SystemObservation, ObservationEvidence)
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
- `brain.planning.*`
- `brain.proposal.*`
- `brain.evaluation.*`
- `brain.governance.*`
- `brain.authorization.*`
- `brain.execution.*`
- Any engine module