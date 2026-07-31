# PMOS-8: Execution Engine

## Purpose
Perform the authorized action — produce observable facts only. Execution is the terminal layer; it owns performance only. Nothing else.

---

## Constitutional Contract

### Consumes
- `AuthorizationToken` (from Authorization Engine)
- `ExecutionPlan` (derived from authorized decision)

### Produces
- `ExecutionResult` — observable facts only
- `ExecutionReceipt` — constitutional proof of execution
- `ExecutionHistory` — immutable audit trail
- `ExecutionArtifact` — produced artifacts
- `ExecutionFailure` — observed failures (facts only)

### Forbidden Responsibilities
- ❌ Reasoning
- ❌ Evaluation
- ❌ Governance
- ❌ Authorization
- ❌ Scheduling
- ❌ Retries
- ❌ Recovery reasoning
- ❌ Optimization
- ❌ Planning
- ❌ Replanning
- ❌ Repository references
- ❌ Orchestration
- ❌ Scheduling
- ❌ Autonomous behavior

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `AuthorizationToken` | `brain.domain.authorization` | Constitutional permission artifact |
| `ExecutionPlan` | `brain.domain.execution` | Immutable execution instruction |
| `ExecutionContext` | `brain.domain.execution` | Runtime context |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `ExecutionResult` | `brain.domain.execution` | Observable facts only |
| `ExecutionReceipt` | `brain.domain.execution` | Constitutional proof |
| `ExecutionHistory` | `brain.domain.execution` | Immutable history |
| `ExecutionArtifact` | `brain.domain.execution` | Produced artifacts |
| `ExecutionFailure` | `brain.domain.execution` | Observed failures (facts only) |
| `ExecutionReceipt` | `brain.domain.execution` | Constitutional proof |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| X-1: Consumes AuthorizationToken only | `ExecutionPlan.authorization_token_id` required; zero Governance/Authorization imports |
| X-2: Performs only approved work | `ExecutionPlan.operation_identifier` immutable; no dynamic work discovery |
| X-3: Never reasons | No `reasoning`, `confidence`, `recommendation`, `explanation` fields |
| X-4: Never evaluates | Zero Evaluation imports; no `score`, `confidence`, `ranking` fields |
| X-5: Never governs | Zero Governance imports; no `decision`, `approval`, `governance` fields |
| X-6: Never authorizes | Zero Authorization imports; no `authorization`, `permission` fields |
| X-7: Deterministic | All models `frozen=True`; same Plan+Token = same Result |
| X-8: Never invents work | No `additional_work`, `expanded_scope`, `extra_operations` fields |
| X-9: Never expands scope | `ExecutionPlan.operation_identifier` immutable |
| X-10: Never modifies Plan | `ExecutionPlan` frozen; `ExecutionResult` separate |
| X-11: Failures are facts | `ExecutionFailure` has `observed_error` only; no `recommendation`, `recovery_plan` |
| X-12: No autonomous retries | No `retry`, `retry_count`, `auto_retry` fields |
| X-13 | No recovery reasoning | No `diagnosis`, `recovery_plan`, `recommendation` fields |
| X-14 | Always stops on failure | `ExecutionResult.is_terminal` includes `failed` |
| X-15 | Observable facts only | No `interpretation`, `confidence`, `probability`, `assessment`, `judgment` |
| X-16 | No interpretation | No `interpretation`, `confidence`, `probability`, `assessment`, `evaluation`, `judgment`, `opinion`, `prediction` |
| X-17 | Result becomes Observation | `ExecutionReceipt`/`Result` structure supports Observation ingestion |
| X-18 | Immutable | All models `frozen=True` |
| X-19 | History append-only | `ExecutionHistory.with_result()` immutable append |
| X-20 | Execution only | No audit/observation/governance ownership |
| X-21 | Receipt is proof | Minimal fields; no reasoning fields |
| X-22 | Authorization + Domain only | Zero Governance/Evaluation/Proposal/Problem/Hypothesis/Observation imports |
| X-23 | Constitutionally minimal | Every field justified by X-1 through X-22 |

---

## Input/Output Specification

### Input: ExecutionContext
```python
@dataclass(frozen=True)
class ExecutionContext:
    execution_plan_id: UUID
    authorization_token_id: UUID
    constitutional_version: str = ""
    metadata: Tuple[Tuple[str, str], ...] = ()
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")
```

### Output: ExecutionResult
```python
@dataclass(frozen=True)
class ExecutionResult:
    execution_result_id: UUID = uuid.uuid4()
    execution_plan_id: UUID
    status: str = "pending"  # ExecutionStatus value
    authorization_token_id: UUID

    # Observable facts only
    artifacts_produced: Tuple[UUID, ...] = ()
    artifact_ids: Tuple[UUID, ...] = ()
    error_report: Optional[str] = None
    failure_type: Optional[str] = None  # FailureType value
    duration_ms: int = 0
    metrics: Tuple[Tuple[str, str], ...] = ()
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.execution_plan_id:
            raise ValueError("execution_plan_id must not be empty")

    @property
    def is_terminal(self) -> bool:
        return self.status in ("completed", "failed", "withdrawn", "superseded")

    @property
    def is_successful(self) -> bool:
        return self.status == "completed"
```

### Output: ExecutionReceipt
```python
@dataclass(frozen=True)
class ExecutionReceipt:
    """
    The constitutional artifact produced by execution.
    ExecutionReceipt is the ONLY artifact Execution is required to produce.
    It is a receipt — proof, not reasoning.
    """
    receipt_id: UUID = uuid.uuid4()
    execution_result_id: UUID
    authorization_token_id: UUID
    issued_at: datetime = datetime.now(timezone.utc)
    constitutional_version: str = "1.0"

    # Observable facts recorded
    execution_duration_ms: int = 0
    artifact_count: int = 0
    status_at_completion: str = "unknown"
    metrics_hash: str = ""

    def __post_init__(self) -> None:
        if not self.constitutional_version.strip():
            raise ValueError("constitutional_version must not be empty")
```

---

## Engine Interface

```python
class ExecutionEngine:
    """
    Constitutional contract: Pure function of AuthorizationToken + ExecutionPlan → ExecutionResult/Receipt.
    No reasoning. No evaluation. No governance. No authorization. No scheduling. No retries. No recovery.
    """
    
    def execute(
        self,
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        Execute the authorized plan.
        
        Must produce ExecutionResult with:
        - Observable facts only (artifacts, duration, status, error)
        - NO confidence, recommendation, reasoning, explanation, interpretation
        - NO scoring, ranking, prioritization
        - NO retry logic, recovery logic, scheduling
        - NO governance, authorization, evaluation logic
        
        Must produce ExecutionReceipt as primary artifact.
        
        Raises:
            AuthorizationTokenInvalidError: Token invalid, revoked, or expired
            ExecutionPlanInvalidError: Plan invalid or superseded
            AuthorizationRevokedError: Authorization revoked
            ConstitutionalViolationError: Plan violates constitutional constraints
        """
        ...
    
    def get_receipt(
        self,
        execution_result_id: UUID
    ) -> ExecutionReceipt:
        """Retrieve the constitutional receipt for a completed execution."""
        ...
    
    def get_history(
        self,
        execution_plan_id: UUID
    ) -> ExecutionHistory:
        """Get execution history for a plan."""
        ...
    
    def get_latest_result(
        self,
        execution_plan_id: UUID
    ) -> Optional[ExecutionResult]:
        """Get latest (non-superseded) result for a plan."""
        ...
```

---

## Quality Gates

### Result Validation
- ✅ `status` in {pending, running, completed, failed, aborted, superseded}
- ✅ `execution_plan_id` required
- ✅ `authorization_token_id` required
- ✅ `artifacts_produced` tuple of UUIDs
- ✅ `artifact_ids` tuple of UUIDs
- ✅ `error_report` only present on failure
- ✅ `failure_type` valid FailureType value
- ✅ `duration_ms` ≥ 0
- ✅ `metrics` tuple of string pairs
- ✅ NO `confidence`, `confidence_score`, `ranking`, `priority`, `severity`, `probability`, `usefulness`
- ✅ NO `approved`, `rejected`, `accepted`, `recommended`
- ✅ NO `execution_plan`, `repository`, `strategy`, `mutation`
- ✅ NO `recommendation`, `suggestion`, `propose`, `decide`, `approve`, `reject`
- ✅ NO `interpretation`, `assessment`, `evaluation`, `judgment`, `opinion`, `prediction`

### Receipt Validation
- ✅ `receipt_id` UUID
- ✅ `execution_result_id` UUID
- ✅ `authorization_token_id` UUID
- ✅ `issued_at` datetime
- ✅ `constitutional_version` non-empty
- ✅ `execution_duration_ms` ≥ 0
- ✅ `artifact_count` ≥ 0
- ✅ `status_at_completion` matches result status
- ✅ `metrics_hash` string
- NO `reasoning`, `evaluation`, `governance`, `decision`, `approval`, `recommendation`, `explanation`, `interpretation`, `analysis`, `judgment`, `assessment`, `strategy`, `plan`, `optimization`, `retries`, `recovery`, `scheduling`, `orchestration`

### History Validation
- ✅ `with_result()` returns new history (immutable append)
- ✅ `execution_count` property
- ✅ `frozen=True`

---

## Engine Interface

```python
class ExecutionEngine:
    """
    Constitutional contract: Pure function of AuthorizationToken + ExecutionPlan → ExecutionResult/Receipt.
    No reasoning. No evaluation. No governance. No authorization. No scheduling. No retries. No recovery.
    """
    
    def execute(
        self,
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        Execute the authorized plan.
        
        Must produce ExecutionResult with:
        - Observable facts only (artifacts, duration, status, error)
        - NO confidence, recommendation, reasoning, explanation, interpretation
        - NO scoring, ranking, prioritization
        - NO retry logic, recovery logic, scheduling
        - NO governance, authorization, evaluation logic
        
        Must produce ExecutionReceipt as primary artifact.
        
        Raises:
            AuthorizationTokenInvalidError: Token invalid, revoked, or expired
            ExecutionPlanInvalidError: Plan invalid or superseded
            AuthorizationRevokedError: Authorization revoked
            ConstitutionalViolationError: Plan violates constitutional constraints
        """
        ...
    
    def get_receipt(
        self,
        execution_result_id: UUID
    ) -> ExecutionReceipt:
        """Retrieve the constitutional receipt for a completed execution."""
        ...
    
    def get_history(
        self,
        execution_plan_id: UUID
    ) -> ExecutionHistory:
        """Get execution history for a plan."""
        ...
    
    def get_latest_result(
        self,
        execution_plan_id: UUID
    ) -> Optional[ExecutionResult]:
        """Get latest (non-superseded) result for a plan."""
        ...
```

---

## Quality Gates

### Result Validation
- ✅ `status` in {pending, running, completed, failed, aborted}
- ✅ `execution_plan_id` required
- ✅ `authorization_token_id` required
- ✅ `artifacts_produced` tuple of UUIDs
- ✅ `artifact_ids` tuple of UUIDs
- ✅ `error_report` only present on failure
- ✅ `failure_type` valid FailureType value
- ✅ `duration_ms` ≥ 0
- ✅ `metrics` tuple of string pairs
- ✅ NO `confidence`, `confidence_score`, `ranking`, `priority`, `severity`, `probability`, `usefulness`
- ✅ NO `approved`, `rejected`, `accepted`, `recommended`
- ✅ NO `execution_plan`, `repository`, `strategy`, `mutation`
- ✅ NO `recommendation`, `suggest`, `propose`, `decide`, `approve`, `reject`
- ✅ NO `interpretation`, `assessment`, `evaluation`, `judgment`, `opinion`, `prediction`

### Receipt Validation
- ✅ `receipt_id`, `execution_result_id`, `authorization_token_id`, `issued_at`, `constitutional_version`
- ✅ NO `execution`, `runtime`, `scheduling`, `retries`, `workflow`, `orchestration`, `plan`, `execution_plan`, `repository`
- ✅ Minimal fields only

### History Validation
- ✅ `with_result()` returns new history (immutable append)
- ✅ `frozen=True` on all models

### Dependency Direction
- ✅ Only imports: `brain.domain.authorization`, `brain.domain.evaluation`, `brain.domain.proposal`, `brain.domain.problem`, `brain.domain.observation`, `brain.domain.execution`, stdlib
- ✅ NO `brain.application`, `brain.runtime`, `brain.adapter`, `brain.repositories`, `brain.infrastructure`, `brain.planning`, `brain.reflection`, `brain.evolution`, `brain.learning`, `brain.execution`, `brain.validation`, `brain.detection`, `brain.retrieval`, `brain.services`, `brain.application.usecases`, `brain.application.workflow`, `brain.application.bridges`

---

## Dependencies

### Allowed
- `brain.domain.authorization` (AuthorizationToken — identifiers only)
- `brain.domain.evaluation` (Evaluation — identifiers only)
- `brain.domain.proposal` (Proposal — identifiers only)
- `brain.domain.problem` (ProblemStatement — identifiers only)
- `brain.domain.observation` (SystemObservation — identifiers only)
- `brain.domain.execution` (ExecutionPlan, ExecutionContext, ExecutionResult, ExecutionReceipt, ExecutionArtifact, ExecutionFailure, ExecutionHistory, ExecutionStatus, ArtifactType, FailureType)
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
- `brain.execution.*` (except own domain models)
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