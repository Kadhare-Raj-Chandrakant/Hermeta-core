# Next Implementation Task

## Current Status
**No active implementation task.** Architecture is frozen and certified.

## Next Milestone Target
**Milestone 26: Integration & System Validation**

---

## Next Implementation Target (When Ready)

### Target: Observation Engine
**Engine Contract:** `PMOS/PMOS-1-OBSERVATION.md`

### Prerequisites (All Complete ✅)
- [x] Observation domain models frozen (4 models)
- [x] Observation Engine contract frozen (PMOS-1)
- [x] Architecture tests passing (test_observation_architecture.py)
- [x] Upstream dependencies: None (entry point)
- [x] Downstream consumers: Hypothesis Engine

### Implementation Requirements
| Requirement | Status |
|-------------|--------|
| Domain models exist | ✅ `ObservationSignal`, `ObservationEvidence`, `SystemObservation`, `ObservationSnapshot` |
| Engine contract frozen | ✅ `PMOS/PMOS-1-OBSERVATION.md` |
| Architecture tests pass | ✅ `test_observation_architecture.py` |
| Dependencies satisfied | ✅ No upstream dependencies |
| Engine contract approved | ✅ Constitutional laws O-1..O-6 |

### Implementation Scope
| Component | File | Status |
|-----------|------|--------|
| ObservationEngine | `src/brain/observation/engine.py` | Not started |
| Signal detector | `src/brain/observation/detectors/` | Not started |
| Evidence builder | `src/brain/observation/evidence/` | Not started |
| Snapshot builder | `src/brain/observation/snapshot/` | Not started |
| Engine tests | `tests/observation/test_engine.py` | Not started |

### Constitutional Compliance Checklist (O-1..O-6)
- [ ] O-1: Output contains only facts, no recommendations
- [ ] O-2: Output contains no decisions
- [ ] O-3: Output contains no solutions
- [ ] O-4: Engine never mutates observed systems
- [ ] O-5: Evidence and interpretation separate
- [ ] O-6: No EvolutionProposal creation

---

## Next Steps (When Implementation Begins)

1. **Create** `src/brain/observation/engine.py` with `ObservationEngine` class
2. **Implement** `observe()` and `observe_batch()` methods
3. **Implement** signal detection and evidence building
-   [ ] `src/brain/observation/detectors/` for signal detection
-   [ ] `src/brain/observation/evidence/` for evidence building
-   [ ] `src/brain/observation/snapshot/` for snapshot building
-   [ ] `tests/observation/test_engine.py` with constitutional compliance tests
-   [ ] `tests/observation/test_detectors.py`
-   [ ] `tests/observation/test_evidence.py`

### Constitutional Compliance Gates
Before merge, all must pass:
- [ ] `test_observation_architecture.py` (existing)
- [ ] New engine tests pass
- [ ] All 1,735 tests pass
- [ ] No constitutional law violations (O-1..O-6)
- [ ] Zero forbidden imports in engine code
- [ ] Zero mutation methods in domain models

---

## Blocking Items
**None.** All architectural prerequisites complete.

---

## When to Begin
Only when explicitly directed to begin Milestone 26. The architecture is frozen; do not begin implementation without explicit direction.