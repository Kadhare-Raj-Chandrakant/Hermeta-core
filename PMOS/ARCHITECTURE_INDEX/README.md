# Architecture Index

## Navigation Structure

This index provides lightweight navigation to the actual architecture documents. It does NOT duplicate architecture — it only indexes it.

---

## Core Architecture Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **HERMES_ARCHITECTURE_STATE.md** | Master architecture document | `docs/HERMES_ARCHITECTURE_STATE.md` |
| **HERMES_CONSTITUTION_CERTIFICATION.md** | B.8 Certification | `docs/HERMES_CONSTITUTION_CERTIFICATION.md` |
| **HERMES_ENGINE_CONTRACTS.md** | 8 Engine Contracts | `docs/HERMES_ENGINE_CONTRACTS.md` |
| **HERMES_CONSTITUTIONAL_PIPELINE.md** | Pipeline Reasoning | `docs/HERMES_CONSTITUTIONAL_PIPELINE.md` |
| **HERMES_STABILIZATION_CERTIFICATION.md** | A.9 Certification | `docs/HERMES_STABILIZATION_CERTIFICATION.md` |
| **HERMES_CONSTITUTION.md** | Constitutional Laws | `FOUNDATION/CONSTITUTION.md` |

---

## Domain Layer Index

| Module | Path | Models | Status |
|--------|------|--------|--------|
| Observation | `src/brain/domain/observation/` | 4 | ✅ Frozen |
| Problem | `src/brain/domain/problem/` | 5 | ✅ Frozen |
| Proposal | `src/brain/domain/proposal/` | 6 | ✅ Frozen |
| Evaluation | `src/brain/domain/evaluation/` | 6 | ✅ Frozen |
| Governance | `src/brain/domain/governance/` | 7 | ✅ Frozen |
| Authorization | `src/brain/domain/authorization/` | 7 | ✅ Frozen |
| Execution | `src/brain/domain/execution/` | 8 | ✅ Frozen |

---

## PMOS Index

| Document | Purpose | Location |
|----------|---------|----------|
| `PMOS/MANIFEST.md` | Entry point | `PMOS/MANIFEST.md` |
| `PMOS/SESSION.md` | Current session | `PMOS/SESSION.md` |
| `PMOS/CURRENT_STATE.md` | Current truth | `PMOS/CURRENT_STATE.md` |
| `PMOS/NEXT_TASK.md` | Next implementation target | `PMOS/NEXT_TASK.md` |
| `PMOS/ARCHITECTURE_FINGERPRINT.md` | Architecture fingerprint | `PMOS/ARCHITECTURE_FINGERPRINT.md` |
| `PMOS/PMOS_VALIDATION.md` | Validation rules | `PMOS/PMOS_VALIDATION.md` |

### Engine Contracts (PMOS)
| Engine | Contract | Location |
|--------|----------|----------|
| Observation | PMOS-1 | `PMOS/PMOS-1-OBSERVATION.md` |
| Hypothesis | PMOS-2 | `PMOS/PMOS-2-HYPOTHESIS.md` |
| Problem | PMOS-3 | `PMOS/PMOS-3-PROBLEM.md` |
| Proposal | PMOS-4 | `PMOS/PMOS-4-PROPOSAL.md` |
| Evaluation | PMOS-5 | `PMOS/PMOS-5-EVALUATION.md` |
| Governance | PMOS-6 | `PMOS/PMOS-6-GOVERNANCE.md` |
| Authorization | PMOS-7 | `PMOS/PMOS-7-AUTHORIZATION.md` |
| Execution | PMOS-8 | `PMOS/PMOS-8-EXECUTION.md` |

---

## Architecture Test Index

| Test Suite | Tests | Purpose |
|------------|-------|---------|
| `test_architecture_setup.py` | 10 | Infrastructure smoke tests |
| `test_boundary_responsibility.py` | 15 | Responsibility boundaries |
| `test_circular_dependencies.py` | 9 | DAG verification |
| `test_constitutional_certification.py` | 23 | B.8 certification |
| `test_controlled_failure_simulation.py` | 58 | A.7 resilience |
| `test_dependency_direction.py` | 14 | DAG direction |
| `test_evaluation_architecture.py` | 14 | E-1..E-16 |
| `test_execution_architecture.py` | 19 | X-1..X-23 |
| `test_forbidden_imports.py` | 4 | Import hygiene |
| `test_governance_architecture.py` | 48 | G-1..G-23 |
| `test_observation_architecture.py` | 10 | O-1..O-6 |
| `test_problem_architecture.py` | 18 | H-1..H-8, P-1..P-12 |
| `test_proposal_architecture.py` | 23 | P-1..P-12 |
| `test_public_api_contract.py` | 40 | Contract boundaries |
| `test_state_ownership.py` | 16 | State ownership |
| `test_authorization_architecture.py` | 28 | A-1..A-16 |
| `test_proposal_architecture.py` | 23 | P-1..P-12 |
| `test_public_api_contract.py` | 40 | Contract boundaries |
| `test_state_ownership.py` | 16 | State ownership |
| **Total** | **420** | |

---

## Documentation Index

| Document | Purpose | Location |
|----------|---------|----------|
| `HERMES_ARCHITECTURE_STATE.md` | Master architecture | `docs/HERMES_ARCHITECTURE_STATE.md` |
| `HERMES_CONSTITUTION_CERTIFICATION.md` | B.8 certification | `docs/HERMES_CONSTITUTION_CERTIFICATION.md` |
| `HERMES_ENGINE_CONTRACTS.md` | 8 engine contracts | `docs/HERMES_ENGINE_CONTRACTS.md` |
| `HERMES_CONSTITUTIONAL_PIPELINE.md` | Pipeline reasoning | `docs/HERMES_CONSTITUTIONAL_PIPELINE.md` |
| `HERMES_STABILIZATION_CERTIFICATION.md` | A.9 certification | `docs/HERMES_STABILIZATION_CERTIFICATION.md` |
| `HERMES_CONSTITUTION.md` | Constitutional laws | `FOUNDATION/CONSTITUTION.md` |
| `HERMES_STABILIZATION_CERTIFICATION.md` | A.9 certification | `docs/HERMES_STABILIZATION_CERTIFICATION.md` |

---

## FOUNDATION Index

| Document | Purpose | Location |
|----------|---------|----------|
| `PROJECT_IDENTITY.md` | What is Hermes | `FOUNDATION/PROJECT_IDENTITY.md` |
| `VISION.md` | Why Hermes exists | `FOUNDATION/VISION.md` |
| `PHILOSOPHY.md` | How Hermes thinks | `FOUNDATION/PHILOSOPHY.md` |
| `CONSTITUTION.md` | Constitutional laws | `FOUNDATION/CONSTITUTION.md` |
| `STRATEGY.md` | Strategic direction | `FOUNDATION/STRATEGY.md` |

---

## PMOS Navigation

```
PMOS/
├── MANIFEST.md                 → Entry point (START HERE)
├── SESSION.md                  → Current session context
├── CURRENT_STATE.md            → Current project truth
├── NEXT_TASK.md                → Next implementation target
├── ARCHITECTURE_FINGERPRINT.md → Architecture fingerprint
├── PMOS_VALIDATION.md          → Validation rules
├── ARCHITECTURE_INDEX/         → This directory
├── PMOS-1-OBSERVATION.md       → Observation Engine
├── PMOS-2-HYPOTHESIS.md        → Hypothesis Engine
├── PMOS-3-PROBLEM.md           → Problem Engine
├── PMOS-4-PROPOSAL.md          → Proposal Engine
├── PMOS-5-EVALUATION.md        → Evaluation Engine
├── PMOS-6-GOVERNANCE.md        → Governance Engine
├── PMOS-7-AUTHORIZATION.md     → Authorization Engine
├── PMOS-8-EXECUTION.md         → Execution Engine
└── PMOS_VALIDATION.md          → Validation rules
```

---

## Quick Reference: Where to Find Anything

| Question | Go To |
|----------|-------|
| "What is Hermes?" | `FOUNDATION/PROJECT_IDENTITY.md` |
| "Why Hermes?" | `FOUNDATION/VISION.md` |
| "How Hermes thinks" | `FOUNDATION/PHILOSOPHY.md` |
| "Constitutional laws" | `FOUNDATION/CONSTITUTION.md` |
| "Strategic direction" | `FOUNDATION/STRATEGY.md` |
| "B.8 Certification" | `docs/HERMES_CONSTITUTION_CERTIFICATION.md` |
| "Engine contracts" | `docs/HERMES_ENGINE_CONTRACTS.md` |
| "Pipeline reasoning" | `docs/HERMES_CONSTITUTIONAL_PIPELINE.md` |
| "Architecture state" | `docs/HERMES_ARCHITECTURE_STATE.md` |
| "Current task" | `PMOS/NEXT_TASK.md` |
| "Current state" | `PMOS/CURRENT_STATE.md` |
| "Engine X contract" | `PMOS/PMOS-X-*.md` |
| "Architecture fingerprint" | `PMOS/ARCHITECTURE_FINGERPRINT.md` |
| "Validation rules" | `PMOS/PMOS_VALIDATION.md` |
| "Traceability chain" | `PMOS/CURRENT_STATE.md` (Traceability Chain section) |
| "Engine X readiness" | `PMOS/PMOS-X-*.md` + `PMOS/CURRENT_STATE.md` |
| "Where is code for X?" | `src/brain/domain/<stage>/` |
| "Test for X" | `tests/architecture/test_*_architecture.py` |

---

## Quick Start for New AI

1. Read `PMOS/MANIFEST.md` (entry point)
2. Read `PMOS/SESSION.md` (session context)
3. Read `PMOS/CURRENT_STATE.md` (current truth)
4. Read `PMOS/NEXT_TASK.md` (what to do next)
5. Follow `NEXT_TASK.md` references

**Stop after step 5 unless `NEXT_TASK.md` references another document.**