# PMOS-7: Authorization Engine

## Purpose
Grant or deny constitutional permission for a governed decision to proceed. Authorization is the final constitutional gate before execution.

---

## Constitutional Contract

### Consumes
- `GovernanceDecision` (from Governance Engine)
- Active authorization policies

### Produces
- `AuthorizationRecord` — immutable constitutional permission
- `AuthorizationContext` — immutable evaluation context
- `AuthorizationHistory` — immutable append-only history
- `AuthorizationConstraint` — constitutional restrictions
- `AuthorizationRationale` — WHY permission granted/denied
- `AuthorizationToken` — constitutional artifact for Execution

### Forbidden Responsibilities
- ❌ Observation collection
- ❌ Hypothesis generation
- ❌ Problem formulation
- ❌ Proposal generation
- ❌ Evaluation
- ❌ Governance
- ❌ Execution
- ❌ Scheduling
- ❌ Retries
- ❌ Workflow state
- ❌ Repository references
- ❌ Planning information
- ❌ Repository references

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `GovernanceDecision` | `brain.domain.governance` | Constitutional decision to authorize |
| `GovernancePolicy` | `brain.domain.governance` | Policies constraining authorization |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `AuthorizationRecord` | `brain.domain.authorization` | Immutable permission |
| `AuthorizationContext` | `brain.domain.authorization` | Evaluation context |
| `AuthorizationHistory` | `brain.domain.authorization` | Immutable history |
| `AuthorizationConstraint` | `brain.domain.authorization` | Constitutional restrictions |
| `AuthorizationRationale` | `brain.domain.authorization` | Justification |
| `AuthorizationToken` | `brain.domain.authorization` | Execution artifact |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| A-1: Consumes GovernanceDecision only | `AuthorizationContext` has `governance_decision_id`; zero Governance imports |
| A-2: Owns permission only | Zero Evaluation/Governance/Execution fields |
| A-3: Never evaluates | Zero Evaluation imports |
| A-4: Never governs | Zero Governance/Decision imports |
| A-5: Never executes | Zero Execution imports |
| A-6: Immutable | All models `frozen=True` |
| A-7: Deterministic | Frozen dataclasses; same inputs = same outputs |
| A-8: Superseded, never mutated | `superseded_by` field; `AuthorizationHistory.with_record()` |
| A-9: Traceability preserved | `governance_decision_id`, `policy_ids`, `constitutional_version` |
| A-10: Never bypasses Governance | `governance_decision_id` required on AuthorizationRecord |
| A-11: Never invents permission | No `create_authorization`, `generate_authorization` fields |
| A-12: Never authorizes violations | `AuthorizationConstraint` with `policy_ids` |
| A-13: Never weakens policy | Context/Constraint require `policy_ids` |
| A-14: Lifecycle independent from Execution | No execution states in `AuthorizationState` enum |
| A-15: Execution consumes Token only | `AuthorizationToken` has minimal fields |
| A-16: No execution metadata | Token/Record/Context have no execution fields |

---

## Input/Output Specification

### Input: AuthorizationRequest
```python
@dataclass(frozen=True)
class AuthorizationRequest:
    governance_decision_id: UUID
    policy_ids: Tuple[UUID, ...]
    constitutional_version: str
    metadata: Tuple[Tuple[str, str], ...] = ()
```

### Output: AuthorizationRecord
```python
@dataclass(frozen=True)
class AuthorizationRecord:
    authorization_id: UUID = uuid.uuid4()
    governance_decision_id: UUID
    state: str = "requires_review"  # AuthorizationState value
    rationale_id: UUID
    issued_at: datetime = datetime.now(timezone.utc)
    constitutional_version: str = "1.0"
    superseded_by: Optional[UUID] = None

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None
```

### Output: AuthorizationToken
```python
@dataclass(frozen=True)
class AuthorizationToken:
    token_id: UUID = uuid.uuid4()
    authorization_record_id: UUID
    issued_at: datetime = datetime.now(timezone.utc)
    constitutional_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")
```

---

## Engine Interface

```python
class AuthorizationEngine:
    """
    Constitutional contract: Pure function of GovernanceDecision → AuthorizationRecord/Token.
    No evaluation logic. No governance logic. No execution logic.
    """
    
    def authorize(
        self,
        request: AuthorizationRequest
    ) -> AuthorizationRecord:
        """
        Determine constitutional permission for a GovernanceDecision.
        
        Must produce AuthorizationRecord with:
        - state (AuthorizationState)
        - rationale_id (linking to AuthorizationRationale)
        - governance_decision_id (traceability)
        - policy_ids (which policies applied)
        
        Must NOT:
        - Contain evaluation logic
        - Contain governance logic
        - Contain execution logic
        - Contain scheduling/orchestration/retry logic
        - Contain repository operations
        - Create new governance decisions
        
        Raises:
            InvalidDecisionError: GovernanceDecision invalid or superseded
            InsufficientPolicyError: No applicable policies
            ConstitutionalViolationError: Decision violates constitutional policy
        """
        ...
    
    def revoke(
        self,
        authorization_id: UUID,
        reason: str
    ) -> AuthorizationRecord:
        """Revoke an authorization (creates superseded record)."""
        ...
    
    def get_active_authorization(
        self,
        governance_decision_id: UUID
    ) -> Optional[AuthorizationRecord]:
        """Get the currently active authorization for a decision."""
        ...
    
    def get_history(
        self,
        governance_decision_id: UUID
    ) -> AuthorizationHistory:
        """Get complete authorization history for a decision."""
        ...
    
    def issue_token(
        self,
        authorization_record_id: UUID
    ) -> AuthorizationToken:
        """Issue AuthorizationToken for an authorized record."""
        ...
```

---

## Quality Gates

### Record Validation
- ✅ `governance_decision_id` required
- ✅ `state` is valid `AuthorizationState`
- ✅ `rationale_id` present
- ✅ `constitutional_version` present
- ✅ No `execution_metadata`, `runtime`, `scheduling`, `retries`, `workflow_state`, `repository`, `planning`, `execution_plan` fields

### Context Validation
- ✅ `governance_decision_id` required
- ✅ `policy_ids` required
- ✅ `constitutional_version` required
- ✅ No `runtime`, `repository`, `execution`, `adapter`, `application` fields

### Token Validation
- ✅ Minimal fields only: `token_id`, `authorization_record_id`, `issued_at`, `constitutional_version`
- ✅ No `execution`, `runtime`, `scheduling`, `retries`, `workflow`, `orchestration`, `plan`, `repository` fields

### History Validation
- ✅ `with_record()` returns new history (immutable append)
- ✅ `constitutional_version` tracked
- ✅ `AuthorizationHistory` frozen

### Constitutional Compliance
- ✅ No Governance imports
- ✅ No Evaluation imports
- ✅ No Execution imports
- ✅ No Proposal imports
- ✅ Zero runtime/application/adapter imports
- ✅ All models `frozen=True`

---

## Dependencies

### Allowed
- `brain.domain.governance` (GovernanceDecision - identifiers only)
- `brain.domain.governance` (GovernancePolicy - identifiers only)
- `brain.domain.authorization` (AuthorizationRecord, AuthorizationContext, AuthorizationHistory, AuthorizationConstraint, AuthorizationRationale, AuthorizationToken)
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
- `brain.application.usecases.*`
- `brain.application.workflow.*`
- `brain.application.bridges.*`
- Any engine module
- Any runtime module
- Any adapter module
- Any repository module
- Any infrastructure module