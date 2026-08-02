# Handoff State — Cold-Start Recovery

## Purpose

This document guarantees that any AI (or human) resuming Hermes Brain development can
recover full working context from repository memory alone, without access to the
previous session transcript.

---

## 1. Project Identity

| Property | Value |
|----------|-------|
| Project | Hermes Brain |
| Repository | `hermes-brain` (git, branch `main`) |
| Phase | Phase B Complete — Phase C Ready |
| Architecture Version | B.8 (Constitutional Certification) — FROZEN |
| Pipeline | 8-stage frozen |
| Constitution | 1.0 (O-1 through X-23), 82 laws |

---

## 2. Milestone History

| Milestone | Status | Tag |
|-----------|--------|-----|
| B.0–B.7 | COMPLETE | — |
| B.8 Constitutional Certification & Freeze | COMPLETE | — |
| post-audit-v1.0 (security & reliability audit fixes) | COMPLETE | `post-audit-v1.0` |
| 26.1 Engine Implementation (8 engines + orchestrator) | COMPLETE | — |
| 26.2 Integration Validation Layer | COMPLETE | — |
| 26.3 Robustness Validation | COMPLETE | `milestone-26.3` |
| 26.4 System Acceptance Audit | COMPLETE | `milestone-26.4` |

---

## 3. Verified Test Baseline

| Suite | Count | Status |
|-------|-------|--------|
| Architecture Tests | 420 | PASS |
| Unit/Integration | 1,480 | PASS |
| **Total** | **1,900** | **ALL PASS** |
| Regressions | 0 | — |

Verification command:

```bash
python -m pytest -q --tb=no
```

---

## 4. Frozen Rules (Constitutional Amendment Required to Change)

- Pipeline stage order: Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
- Dependency direction: same order, never reversed
- Stage ownership: each model has exactly one owner stage
- Dependency graph: DAG, no cycles
- Constitutional laws: 82 (O-1 through X-23)
- Domain model immutability: all domain models are `@dataclass(frozen=True)`
- History mutability: append-only (supersession, never mutation)
- Traceability: every artifact traces to an originating observation
- Stage separation: no stage imports from downstream stages
- Engine contracts: 8 contracts frozen with exact I/O

Forbidden during any future milestone unless explicitly amended:
- Adding/removing pipeline stages
- Changing dependency direction
- Modifying constitutional laws
- Changing stage ownership
- Modifying the traceability chain
- Altering frozen dataclass structure

---

## 5. Current Milestone Status

- **Milestone 26.4 (System Acceptance Audit): COMPLETE**
- Acceptance audit: 10 areas, all PASS
- Cold-start recovery: verified (this document + navigation chain)
- Architecture unchanged since `milestone-26.3` (zero src/ or tests/ diffs)

---

## 6. Next Milestone

**Milestone 27: Production Hardening, Documentation, and Final Certification.**

Follow `PMOS/NEXT_TASK.md` — it is the single approved implementation target.

---

## 7. Cold-Start Recovery Sequence (Mandatory)

1. Read `PMOS/MANIFEST.md`
2. Read `PMOS/SESSION.md`
3. Read `PMOS/CURRENT_STATE.md`
4. Read `PMOS/NEXT_TASK.md`
5. Stop at NEXT_TASK unless it references another document
6. Run `python -m pytest -q --tb=no` to confirm the 1,900-test baseline
7. Begin the single approved target in NEXT_TASK.md

---

## 8. Conflict Resolution

If repository state conflicts with this document, STOP and report the conflict.
Never guess. Never duplicate. Follow the MANIFEST navigation chain.

---

**Status: HANDOFF READY — MILESTONE 26.4 COMPLETE — READY FOR MILESTONE 27**
