# PMOS-2: Hypothesis Engine

## Purpose
Generate competing explanations for observed facts. The Hypothesis Engine is the constitutional creative layer — it produces competing explanations without selecting winners.

---

## Constitutional Contract

### Consumes
- `SystemObservation` (from Observation Engine)
- `ObservationEvidence` (supporting metadata)
- Active hypothesis policies (generation rules, diversity requirements)

### Produces
- `Hypothesis` — one possible explanation for observations
- `HypothesisSpace` — collection of competing hypotheses for the same observations

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Problem formulation
- ❌ Proposal generation
- ❌ Evaluation
- ❌ Governance
- ❌ Authorization
- ❌ Execution
- ❌ Ranking or selection of hypotheses

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `SystemObservation` | `brain.domain.observation` | Raw facts to explain |
| `ObservationEvidence` | `brain.domain.observation` | Supporting evidence for observations |
| `HypothesisPolicy` | `brain.domain.problem` | Generation rules, diversity requirements |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `Hypothesis` | `brain.domain.problem` | One possible explanation for observations |
| `HypothesisSpace` | `brain.domain.problem` | Collection of competing hypotheses |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| H-1: Hypothesis is not a solution | No `recommendation`, `execution`, `mutation` fields |
| H-2: Multiple hypotheses per observation | `HypothesisSpace` holds tuple of `Hypothesis`; no ranking/selection |
| H-3: ProblemStatement references multiple hypotheses | `ProblemStatement.hypothesis_space_id` links to space |
| H-4: Observations immutable | No mutation methods; `supporting_observation_ids` are immutable UUIDs |
| H-6: No execution info | No `proposal_id`, `execution_plan`, `governance` fields |
| H-7: Independent from Proposal | No imports from `brain.domain.proposal` |

---

## Input/Output Specification

### Input: HypothesisRequest
```python
@dataclass(frozen=True)
class HypothesisRequest:
    observations: Tuple[SystemObservation, ...]  # Observations to explain
    evidence: Tuple[ObservationEvidence, ...]    # Supporting evidence
    policy: HypothesisPolicy                      # Generation rules
    context: Tuple[str, ...] = ()                 # Additional context
```

### Output: HypothesisSpace
```python
@dataclass(frozen=True)
class HypothesisSpace:
    space_id: UUID
    observation_ids: Tuple[UUID, ...]            # Observations being explained
    hypotheses: Tuple[Hypothesis, ...]           # Competing explanations
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Output: Hypothesis
```python
@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: UUID
    title: str
    description: str
    confidence: float                              # 0.0 - 1.0
    category: HypothesisCategory                   # CAUSAL, CORRELATIONAL, STRUCTURAL, BEHAVIORAL, ENVIRONMENTAL, UNKNOWN
    supporting_observation_ids: Tuple[UUID, ...]   # Traceability to observations
    created_at: datetime
    metadata: Tuple[Tuple[str, str], ...] = ()
```

---

## Engine Interface

```python
class HypothesisEngine:
    """
    Constitutional contract: Pure function of observations + policy → hypothesis space.
    No state. No side effects. No ranking. No selection.
    """
    
    def generate(
        self,
        request: HypothesisRequest
    ) -> HypothesisSpace:
        """
        Generate competing hypotheses for the given observations.
        
        Must produce at least 2 hypotheses when policy requires diversity.
        Must not rank, score, or select among generated hypotheses.
        
        Raises:
            InsufficientObservationsError: Insufficient evidence for hypothesis generation
            PolicyViolationError: Request violates hypothesis policy
        """
        ...
    
    def extend_space(
        self,
        space: HypothesisSpace,
        additional_observations: Sequence[SystemObservation],
        policy: HypothesisPolicy
    ) -> HypothesisSpace:
        """Extend an existing hypothesis space with new observations."""
        ...
```

---

## Quality Gates

### Hypothesis Validation
- ✅ Title present and non-empty
- ✅ Description present and non-empty
- ✅ Confidence in [0.0, 1.0]
- ✅ Category is valid HypothesisCategory
- ✅ Supporting observation IDs non-empty
- ✅ No recommendation fields
- ✅ No execution fields
- ✅ No decision fields

### Space Validation
- ✅ At least 2 hypotheses when policy requires diversity
- ✅ All hypotheses reference same observation_ids
- ✅ No duplicate hypothesis_ids
- ✅ Space created after all observations

### Constitutional Compliance
- ✅ No ranking/sorting/selection methods
- ✅ No `score`, `rank`, `priority`, `best` fields
- ✅ No evaluation logic
- ✅ No governance logic
- ✅ No execution logic
- ✅ No proposal logic

---

## Dependencies

### Allowed
- `brain.domain.problem` (Hypothesis, HypothesisSpace, HypothesisCategory)
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