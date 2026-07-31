# PMOS-6: Governance Engine

## Purpose
Determine constitutional permissibility of evaluated proposals. Governance is the constitutional authority — it decides what is permissible, not what is optimal.

---

## Constitutional Contract

### Consumes
- `EvaluationSpace` (from Evaluation Engine)
- Active constitutional policies

### Produces
- `GovernanceDecision` — constitutional outcome (APPROVED/REJECTED/DEFERRED/...)
- `GovernanceRationale` — structured justification with constitutional basis
- `GovernanceFinding` — structured constitutional observations
- `GovernanceHistory` — immutable decision record

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Hypothesis generation
- ❌ Problem formulation
- ❌ Proposal generation
- ❌ Evaluation
- ❌ Authorization
- ❌ Execution
- ❌ Optimization
- ❌ Retry logic
- ❌ Recovery reasoning
- ❌ Proposal ranking
- ❌ Proposal scoring
- ❌ Proposal optimization
- ❌ Execution planning
- ❌ Scheduling
- ❌ Retry systems

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `EvaluationSpace` | `brain.domain.evaluation` | Evaluations to adjudicate |
| `GovernancePolicy` | `brain.domain.governance` | Constitutional policies |
| `GovernanceDecision` | `brain.domain.governance` | Previous decisions for consistency |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `GovernanceDecision` | `brain.domain.governance` | Constitutional outcome |
| `GovernanceRationale` | `brain.domain.governance` | Justification with constitutional basis |
| `GovernanceFinding` | `brain.domain.governance` | Constitutional observations |
| `GovernanceHistory` | `brain.domain.governance` | Immutable decision record |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| G-1: Governance consumes Evaluation only | Zero Proposal/Evaluation/Execution imports in logic |
| G-2: Governance never evaluates | No evaluation logic in governance models |
| G-3: Governance never creates proposals | No `create_proposal`, `generate_proposal` fields |
| G-4: Governance never executes | No `execution_plan`, `execution`, `mutation` fields |
| G-5: Every decision references evidence | `rationale_id` + `evidence_ids` mandatory |
| G-6: Every decision references policies | `policy_ids` mandatory |
| G-7: Deterministic | All models `frozen=True` |
| G-8: Deferral supported | `DecisionState.DEFERRED` state |
| G-9: Rejected immutable | `REJECTED` state + `superseded_by` |
| G-10: Explainable | `GovernanceRationale.explanation` + `constitutional_basis` |
| G-11: Never mutates Evaluation | No Evaluation imports in decision logic |
| G-12: Never mutates Proposal | No Proposal imports in decision logic |
| G-13: One active decision per Evaluation | `evaluation_id` unique in active decisions |
| G-14: History immutable | `GovernanceHistory` frozen + append-only `with_decision` |
| G-15: Constitution overrides optimization | `PolicyCategory` only constitutional categories |
| G-16: Never bypasses policy | `DecisionContext` requires `policy_ids` |
| G-17: Never invents evidence | `supporting_evidence_ids` trace to existing |
| G-18: Owns decisions only | No execution fields, no planning fields |
| G-19: Never optimizes | No `optimize`, `optimal`, `best_score` patterns |
| G-20: Decision ≠ Rationale | Separate models; Decision has `rationale_id`, Rationale has no state |
| G-21: Policies immutable | `GovernancePolicy` frozen |
| G-22: Deterministic | All models frozen; same inputs = same outputs |
| G-23: Never creates rules | No `create_policy`, `modify_policy`, `amend_constitution` |

---

## Input/Output Specification

### Input: GovernanceRequest
```python
@dataclass(frozen=True)
class GovernanceRequest:
    evaluation_space_id: UUID
    policy_ids: Tuple[UUID, ...]
    constitutional_version: str
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Output: GovernanceDecision
```python
@dataclass(frozen=True)
class GovernanceDecision:
    decision_id: UUID
    evaluation_id: UUID
    state: str  # DecisionState value: APPROVED, REJECTED, DEFERRED, INSUFFICIENT_EVIDENCE, CONSTITUTIONAL_CONFLICT, REQUIRES_REVIEW, WITHDRAWN, SUPERSEDED
    rationale_id: UUID
    policy_ids: Tuple[UUID, ...]
    created_at: datetime
    superseded_by: Optional[UUID] = None
    decision_mode: str = "constitutional"  # DecisionMode value

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None
```

### Output: GovernanceRationale
```python
@dataclass(frozen=True)
class GovernanceRationale:
    rationale_id: UUID
    explanation: str
    supporting_evidence_ids: Tuple[UUID, ...] = ()
    constitutional_interpretations: Tuple[str, ...] = ()
    findings: Tuple[UUID, ...] = ()  # GovernanceFinding IDs
    constitutional_basis: Tuple[str, ...] = ()
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.explanation.strip():
            raise ValueError("explanation must not be empty")
```

### Supporting Models
```python
@dataclass(frozen=True)
class GovernanceFinding:
    finding_id: UUID
    title: str
    description: str
    severity: str  # FindingSeverity: INFO, WARNING, CRITICAL, BLOCKING
    policy_ids: Tuple[UUID, ...] = ()
    evidence_ids: Tuple[UUID, ...] = ()
    created_at: datetime

@dataclass(frozen=True)
class GovernancePolicy:
    policy_id: UUID
    identifier: str
    title: str
    description: str
    category: str  # PolicyCategory: ARCHITECTURAL_INTEGRITY, STATE_OWNERSHIP, DEPENDENCY_DIRECTION, TRANSACTION_BOUNDARIES, FAILURE_ISOLATION, RECOVERY_OWNERSHIP, CONTRACT_COMPLIANCE, EVOLUTION_SAFETY
    governing_principle: str
    version: str = "1.0"
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier must not be empty")
        if not self.governing_principle.strip():
            raise ValueError("governing_principle must not be empty")

@dataclass(frozen=True)
class DecisionContext:
    evaluation_id: UUID
    proposal_ids: Tuple[UUID, ...]
    policy_ids: Tuple[UUID, ...]
    constitutional_version: str
    metadata: Tuple[Tuple[str, str], ...] = ()
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")
```

### Output: GovernanceHistory
```python
@dataclass(frozen=True)
class GovernanceHistory:
    history_id: UUID
    decision_ids: Tuple[UUID, ...] = ()
    constitutional_version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def with_decision(self, decision_id: UUID) -> "GovernanceHistory":
        return GovernanceHistory(
            history_id=uuid.uuid4(),
            decision_ids=self.decision_ids + (decision_id,),
            constitutional_version=self.constitutional_version,
            created_at=self.created_at,
        )
```

---

## Engine Interface

```python
class GovernanceEngine:
    """
    Constitutional contract: Pure constitutional function of EvaluationSpace → GovernanceDecision.
    No evaluation logic. No proposal logic. No execution logic. Pure constitutional adjudication.
    """
    
    def adjudicate(
        self,
        request: GovernanceRequest
    ) -> GovernanceDecision:
        """
        Adjudicate an evaluation against constitutional policy.
        
        Must produce GovernanceDecision with:
        - state (DecisionState)
        - rationale_id (linking to GovernanceRationale)
        - policy_ids (which policies applied)
        - superseded_by (if superseding prior decision)
        
        Must NOT:
        - Contain evaluation logic
        - Contain proposal generation logic
        - Contain execution logic
        - Contain ranking/selection/optimization logic
        - Contain retry/recovery logic
        - Create proposals
        - Evaluate proposals
        - Execute anything
        
        Raises:
            InsufficientEvidenceError: Evaluation insufficient for decision
            PolicyConflictError: Conflicting constitutional policies
            InsufficientPolicyError: No applicable policies
        """
        ...
    
    def review(
        self,
        decision_id: UUID,
        new_evidence: Tuple[UUID, ...]
    ) -> GovernanceDecision:
        """Review a decision with new evidence. Returns new decision (supersedes old)."""
        ...
    
    def supersede(
        self,
        decision_id: UUID,
        new_decision: GovernanceDecision
    ) -> GovernanceDecision:
        """Supersede a decision (immutable history)."""
        ...
    
    def get_history(
        self,
        evaluation_id: UUID
    ) -> GovernanceHistory:
        """Get complete decision history for an evaluation."""
        ...
    
    def get_active_decision(
        self,
        evaluation_id: UUID
    ) -> Optional[GovernanceDecision]:
        """Get the currently active decision for an evaluation."""
        ...
```

---

## Quality Gates

### Decision Validation
- ✅ `state` is valid `DecisionState` value
- ✅ `rationale_id` present and valid
- ✅ `policy_ids` non-empty tuple
- ✅ `evaluation_id` valid UUID
- ✅ No `execution_plan`, `execution`, `mutation`, `repository` fields
- ✅ No `proposal_creation`, `evaluation_logic`, `governance_logic` fields
- ✅ `superseded_by` is UUID or None

### Rationale Validation
- ✅ `explanation` non-empty string
- ✅ `supporting_evidence_ids` traceable
- ✅ `constitutional_basis` non-empty
- ✅ `findings` reference `GovernanceFinding` IDs
- ✅ No `state`, `approved`, `rejected`, `decision_state` fields

### History Integrity
- ✅ `GovernanceHistory` frozen
- ✅ `with_decision()` returns new history (immutable)
- ✅ `constitutional_version` tracked
- ✅ `decision_ids` immutable tuple

### Constitutional Compliance
- ✅ No `brain.evaluation` imports in governance logic
- ✅ No `brain.proposal` imports in governance logic
- ✅ No `brain.execution` imports
- ✅ No `brain.runtime` imports
- ✅ No `brain.application` imports
- ✅ All models `frozen=True`
- ✅ Deterministic: same inputs → same outputs

---

## Dependencies

### Allowed
- `brain.domain.governance` (Decision, Rationale, Finding, Policy, History, Context)
- `brain.domain.evaluation` (EvaluationSpace - identifiers only)
- `brain.domain.proposal` (ProposalSpace - identifiers only)
- `brain.domain.problem` (ProblemStatement - identifiers only)
- `brain.domain.observation` (SystemObservation - identifiers only)
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
- `brain.proposal.*` (logic)
- `brain.evaluation.*` (logic)
- `brain.execution.*` (logic)
- Any engine module