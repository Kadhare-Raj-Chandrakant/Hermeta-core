# PMOS Manifest

## Project Memory Operating System — Entry Point

This is the single entry point for any AI resuming Hermes development.

---

## Quick Start (Read in Order)

1. **MANIFEST.md** ← You are here
2. **SESSION.md** → Current session context
3. **CURRENT_STATE.md** → Current project truth
4. **NEXT_TASK.md** → Exactly one approved implementation target

---

## Quick Reference

| Question | Answer Location |
|----------|----------------|
| What is Hermes? | `FOUNDATION/PROJECT_IDENTITY.md` |
| Why Hermes exists | `FOUNDATION/VISION.md` |
| How Hermes thinks | `FOUNDATION/PHILOSOPHY.md` |
| What governs Hermes | `FOUNDATION/CONSTITUTION.md` |
| Strategic direction | `FOUNDATION/STRATEGY.md` |
| Current task | `PMOS/NEXT_TASK.md` |
| Current state | `PMOS/CURRENT_STATE.md` |
| Architecture reference | `PMOS/ARCHITECTURE_INDEX/` |
| Engine contracts | `PMOS/PMOS-1-OBSERVATION.md` … `PMOS-8-EXECUTION.md` |
| Validation rules | `PMOS/PMOS_VALIDATION.md` |

---

## Critical Rules (Read Before Continuing)

1. **Read in order**: MANIFEST → SESSION → CURRENT_STATE → NEXT_TASK
4. **Stop at NEXT_TASK** — only continue if it references another document
5. **Never guess** — if repository state conflicts, STOP and report conflict
6. **Never duplicate** — check CURRENT_STATE before implementing
7. **Follow pointers** — only follow references from NEXT_TASK
8. **Single source of truth** — each fact has exactly one owner

---

## Architecture Fingerprint

| Property | Value |
|----------|-------|
| Architecture Version | B.8 (Constitutional Certification) |
| Pipeline Version | 8-stage frozen |
| Constitution Version | 1.0 (O-1 through X-23) |
| Pipeline Stages | 8 (Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution) |
| Domain Models | 43 frozen dataclasses |
| Architecture Tests | 420 passing |
| Total Tests | 1,900 passing |
| Constitutional Laws | 82 (O-1 through X-23) |
| Frozen Layers | Domain, Engine Contracts, Pipeline Order, Dependency Direction |

---

## Current Status (from CURRENT_STATE.md)

| Aspect | Status |
|--------|--------|
| Project Status | CERTIFIED COMPLETE |
| Architecture | FROZEN (B.8 Certified) |
| Phase B | COMPLETE (B.0–B.7) |
| Next Milestone | None — certified complete |
| Domain Models | 43 frozen dataclasses across 8 stages |
| Architecture Tests | 420 passing |
| Total Tests | 1,900 passing |
| Regressions | 0 |

---

## Quick Navigation

| Need | Go To |
|------|-------|
| "What am I building?" | `FOUNDATION/VISION.md` |
| "Why this architecture?" | `FOUNDATION/PHILOSOPHY.md` |
| "What are the laws?" | `FOUNDATION/CONSTITUTION.md` |
| "Where am I?" | `PMOS/CURRENT_STATE.md` |
| "What do I do next?" | `PMOS/NEXT_TASK.md` |
| "How does X engine work?" | `PMOS/PMOS-1-OBSERVATION.md` … `PMOS-8-EXECUTION.md` |
| "Is this allowed?" | `PMOS/PMOS_VALIDATION.md` |
| "Where is the code?" | `PMOS/ARCHITECTURE_FINGERPRINT.md` |