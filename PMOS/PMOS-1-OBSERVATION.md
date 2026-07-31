# PMOS-1: Observation Engine

## Purpose
Detect, validate, and record raw signals from the environment. The Observation Engine is the constitutional entry point — the only component that interfaces with raw external input.

---

## Constitutional Contract

### Consumes
- Raw environmental input (stdin, files, API events, telemetry, user input)
- Active observation policies (what to observe, sampling rates, quality thresholds)

### Produces
- `ObservationSignal` — raw measured facts with metadata
- `ObservationEvidence` — supporting metadata (sample count, measurement period, reliability)

### Forbidden Responsibilities
- ❌ Interpretation of signals
- ❌ Hypothesis formation
- ❌ Problem identification
- ❌ Proposal generation
- ❌ Evaluation
- ❌ Governance
- ❌ Authorization
- ❌ Execution
- ❌ Storage beyond ephemeral buffering

---

## Domain Contracts

### Consumes (Domain Models)
| Model | Source | Purpose |
|-------|--------|---------|
| `ObservationPolicy` | `brain.domain.observation` | Defines what to observe, how often, quality thresholds |
| `SignalCategory` | `brain.domain.observation.enums` | Classifies signal type |

### Produces (Domain Models)
| Model | Destination | Purpose |
|-------|-------------|---------|
| `ObservationSignal` | `brain.domain.observation` | Raw measured fact with category, source, value, unit, timestamp |
| `ObservationEvidence` | `brain.domain.observation` | Sample count, measurement period, reliability, metadata |
| `SystemObservation` | `brain.domain.observation` | Aggregated observation for downstream consumption |

---

## Constitutional Laws Enforced

| Law | Enforcement Mechanism |
|-----|----------------------|
| O-1: Observation describes facts only | No recommendation/decision/solution fields in output models |
| O-2: Observation contains no decisions | Output models have no decision/recommendation fields |
| O-3: Observation contains no solutions | Output models have no solution/recommendation fields |
| O-4: Observation cannot mutate observed systems | Domain models are frozen; no mutation methods |
| O-5: Evidence and interpretation separate | `ObservationEvidence` separate from `ObservationSignal`; no interpretation fields |
| O-6: No EvolutionProposal creation | No imports from evolution/proposal modules |

---

## Input/Output Specification

### Input: RawEnvironmentalInput
```python
# Not a domain model — raw external input
class RawEnvironmentalInput:
    source: str                    # "stdin", "file:/path", "api:/endpoint", "telemetry"
    payload: bytes                 # Raw bytes
    metadata: Dict[str, str]       # Headers, content-type, timestamps
    received_at: datetime          # Wall-clock receipt time
```

### Output: SystemObservation
```python
# Domain model — produced by Observation Engine
@dataclass(frozen=True)
class SystemObservation:
    observation_id: UUID
    category: ObservationCategory    # OPERATIONAL, COGNITIVE, EVOLUTION_HISTORY
    signal: ObservationSignal
    evidence: ObservationEvidence
    confidence: float                # 0.0 - 1.0
    detected_at: datetime
    detection_source: str            # Engine identifier
```

---

## Engine Interface

```python
class ObservationEngine:
    """
    Constitutional contract: Pure function of input + policy → observation.
    No state. No side effects. No persistence.
    """
    
    def observe(
        self,
        raw_input: RawEnvironmentalInput,
        policy: ObservationPolicy
    ) -> SystemObservation:
        """
        Detect, validate, and record a raw signal.
        
        Raises:
            ValidationError: Signal fails policy quality thresholds
            InsufficientEvidenceError: Evidence below policy threshold
        """
        ...
    
    def observe_batch(
        self,
        raw_inputs: Sequence[RawEnvironmentalInput],
        policy: ObservationPolicy
    ) -> Sequence[SystemObservation]:
        """Process multiple inputs atomically."""
        ...
```

---

## Quality Gates

### Signal Validation
- ✅ Source identifier present and non-empty
- ✅ Metric name present and non-empty
- ✅ Value is valid for declared type
- ✅ Unit is recognized or declared custom
- ✅ Timestamp is valid and not in future

### Evidence Validation
- ✅ Sample count ≥ policy minimum
- ✅ Measurement period ≥ policy minimum
- ✅ Confidence in [0.0, 1.0]
- ✅ Metadata keys/values are strings

### Constitutional Compliance
- ✅ No recommendation fields in output
- ✅ No decision fields in output
- ✅ No solution fields in output
- ✅ No evaluation logic in engine
- ✅ No governance logic in engine
- ✅ No execution logic in engine

---

## Dependencies

### Allowed
- `brain.domain.observation` (Signal, Evidence, SystemObservation, Category)
- `brain.domain.references` (Evidence, Relationship)
- `brain.domain.enums` (SignalCategory, ObservationCategory)
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
- Any engine module