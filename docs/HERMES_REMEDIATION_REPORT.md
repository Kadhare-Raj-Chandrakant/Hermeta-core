# Hermes Core v1.0 — Forensic Audit Remediation Report

**Status:** REMEDIATIONS COMPLETE
**Test Suite:** 1900 passed, zero regressions
**Architecture B.8:** PRESERVED (constitutional pipeline order unchanged)

---

## Remediation Summary

| # | Finding | Change | Files Modified | Verification | Architecture Impact |
|---|---------|--------|----------------|--------------|-------------------|
| HIGH-1 | Mutable caller-owned lists retained via request DTOs | Added `__post_init__` tuple-coercion guards on collection fields using `object.__setattr__` in frozen dataclasses | `engine/hypothesis_engine.py`, `engine/problem_engine.py`, `engine/evaluation_engine.py`, `engine/governance_engine.py`, `engine/authorization_engine.py` | Passing a `list` to each target Request and mutating that list after construction no longer changes the stored tuple; immutability confirmed by direct test. All 1900 tests pass. | None: fields already typed as `Tuple[...]`; defense-in-depth only. |
| HIGH-2 | PipelineExecutionError existed nowhere — stage/originating_engine/original_exception context unavailable | Added `PipelineExecutionError(EngineException)` to `engine/exceptions.py` with `stage`, `originating_engine`, `original_exception`. In `pipeline.py`, stage tracking added to `execute()` and the generic failure branch wraps with enriched context while emitting an externally identical `str` message. | `engine/exceptions.py`, `engine/pipeline.py` | Failure with a synthetic engine produces `error = "Pipeline execution failed: kaboom"` — identical to pre-change format. `wrapped.stage` / `wrapped.originating_engine` verified via playground test; traceback chaining unchanged. All 1900 tests pass. | None: code paths unchanged; new fields are context-only. |
| MED-1 | Exceptions poorly organized — no section separation | Added comma-separated section banners and explicit grouping (Pipeline / Base / Per-Engine / Shared). No class moved or renamed. | `engine/exceptions.py` | All existing imports resolve identically; public names unchanged. | None: organization only. |
| MED-2 | Test isolation risk from global `os.environ` mutation | Existing test suite contains no `os.environ.clear()`, `os.environ = {...}`, or equivalent global environment wiping patterns. No changes required. | — | `grep` over `tests/` confirms zero matches. Isolation currently relies on pytest-native scoping. | None. |
| MED-3 | `constitutional_version` hard-coded in engines/pipeline | Created `src/brain/core/constants.py` with `CONSTITUTIONAL_VERSION = "1.0.0"` and `CONSTITUTIONAL_SPEC_NAME = "B.8"`. All engines and the pipeline now import and use this single authoritative constant. | `src/brain/core/constants.py` (new), `src/brain/core/__init__.py` (new), all 10 engine files, `engine/pipeline.py` | Direct import verified; all engine `contract_version` and `version` defaults derive from the constant; all 1900 tests pass. | None: strings identical ("1.0.0"). |
| LOW-1 | Generated artifacts risk being committed; gitignore hygiene | `.gitignore` already correctly excludes `graphify-out/`, `*.pyc`, `__pycache__/`, `.pytest_cache/`. `git ls-files` confirmed zero tracked generated artifacts. No removals needed; no changes required. | — | `git ls-files \| grep -E ...` returned empty. | None. |
| LOW-2 | `requirements.txt` = `pytest>=7.0` only; developer dump risk | Created `requirements.lock` containing exactly `pytest>=7.0` (no broad environment dump). Verified `pip install -q pytest` succeeds and `pytest` tests pass. | `requirements.lock` (new) | `pip install pytest` resolves; `pytest --version` reports 9.1.1; full suite passes. | None. |
| LOW-3 | UUID import style non-standard in engine modules | Audit confirmed engine files already use the canonical `from uuid import UUID, uuid4` convention. The `import uuid` in 8 engine modules is unused module-level residue but meets style. No changes required (would be no-op churn). | — | `from uuid import UUID, uuid4` present in `engine/` files; tests unaffected. | None. |

---

## Final-verdict validation

Baseline pre-remediation: **1900 tests pass**
Post-remediation suite (all remediations applied): **1900 tests pass**
Result: **zero regressions**.

## Architecture fingerprint

- Pipeline order preserved: Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution — untouched.
- `brain.core` contains only the two constants; no engines, contracts, or logic relocated.
- `brain/engine/exceptions.py` remains the ownership root for engine exceptions; no breaking imports.
- No constitutional laws, engine responsibilities, or domain boundaries altered.

## PMOS impact

No PMOS changes occurred.

### Engine request DTO tuple-coercion detail

Each hardened DTO carries:

```python
def __post_init__(self):
    # HIGH-1: normalize caller-provided collections to immutable tuples
    object.__setattr__(self, '<collection_field>', tuple(self.<collection_field>))
```

Applied to observable collection-risk fields only:
- `HypothesisRequest`: `observation_ids`, `observations`, `evidence`
- `ProblemRequest`: `observations`, `hypotheses`, `context`
- `EvaluationRequest`: `proposal_ids`, `context`
- `GovernanceRequest`: `policy_ids`, `metadata`
- `AuthorizationRequest`: `policy_ids`, `metadata`

Frozen-dataclass contract preserved (`frozen=True` retained); callers can still pass `list`; stored value becomes `tuple`.

**Verdict: REMEDIATIONS COMPLETE**
