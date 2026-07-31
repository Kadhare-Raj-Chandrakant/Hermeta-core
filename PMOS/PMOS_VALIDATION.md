# PMOS Validation Rules

## Purpose

This document specifies the manual validation rules for the Project Memory Operating System (PMOS). It is a specification — NOT executable tooling.

---

## Validation Rules

### 1. Single Source of Truth

| Fact | Authoritative Location | Forbidden Elsewhere |
|------|------------------------|---------------------|
| Current milestone | `PMOS/CURRENT_STATE.md` | SESSION, NEXT_TASK, MANIFEST |
| Next implementation | `PMOS/NEXT_TASK.md` | SESSION, CURRENT_STATE, MANIFEST |
| Architecture | `docs/HERMES_ARCHITECTURE_STATE.md` | PMOS, SESSION, CURRENT_STATE |
| Reports | `reports/` | PMOS, docs/ |
| Roadmap | `ROADMAP.md` | PMOS, docs/ |
| Decisions | `ADRs/` | PMOS, docs/ |
| Constitutional laws | `FOUNDATION/CONSTITUTION.md` | docs/, PMOS/ |
| Engine contracts | `PMOS/PMOS-*-ENGINE.md` | docs/, PMOS/ |
| Pipeline reasoning | `docs/HERMES_CONSTITUTIONAL_PIPELINE.md` | PMOS/, docs/ |

**Rule**: If a fact appears in two places with different values, STOP. Resolve before continuing.

---

### 2. No Duplicate Facts

**Check before writing any fact:**
- Does this fact already exist in its authoritative location?
- If YES: STOP. Reference it instead.
- If NO: Write it in its authoritative location only.

**Common duplicates to avoid:**
- Milestone status in multiple places
- Test counts in multiple places
- Architecture status in multiple places
- Engine readiness in multiple places

---

### 3. Pointer Integrity

**Every pointer must resolve:**

| Pointer | From | To | Must Resolve |
|---------|------|-----|-------------|
| MANIFEST → SESSION | `PMOS/MANIFEST.md` | `PMOS/SESSION.md` | ✅ |
| MANIFEST → CURRENT_STATE | `PMOS/MANIFEST.md` | `PMOS/CURRENT_STATE.md` | ✅ |
| MANIFEST → NEXT_TASK | `PMOS/MANIFEST.md` | `PMOS/NEXT_TASK.md` | ✅ |
| SESSION → CURRENT_STATE | `PMOS/SESSION.md` | `PMOS/CURRENT_STATE.md` | ✅ |
| SESSION → NEXT_TASK | `PMOS/SESSION.md` | `PMOS/NEXT_TASK.md` | ✅ |
| CURRENT_STATE → NEXT_TASK | `PMOS/CURRENT_STATE.md` | `PMOS/NEXT_TASK.md` | ✅ |
| NEXT_TASK → Architecture | `PMOS/NEXT_TASK.md` | `docs/HERMES_*.md` | ✅ |
| Architecture Fingerprint → Architecture | `PMOS/ARCHITECTURE_FINGERPRINT.md` | `docs/HERMES_*.md` | ✅ |

**If a pointer is broken: STOP. Fix before continuing.**

---

### 4. Linear Navigation

**Navigation must follow the chain:**

```
MANIFEST → SESSION → CURRENT_STATE → NEXT_TASK → Referenced Document
```

**Never skip levels.**
**Never jump sideways.**
**Never read everything.**

---

### 5. Single Source of Truth Audit

**Run this check before any commit:**

```bash
# Check for duplicate milestone status
grep -r "B.8" docs/ PMOS/ FOUNDATION/ | grep -v ".pyc" | grep -v __pycache__

# Check for duplicate test counts
grep -r "1735\|1735\|420" docs/ PMOS/ FOUNDATION/ | grep -v ".pyc" | grep -v __pycache__

# Check for duplicate architecture status
grep -r "COMPLETE\|FROZEN\|CERTIFIED" docs/ PMOS/ FOUNDATION/ | grep -v ".pyc" | grep -v __pycache__
```

**If duplicates found with different values: STOP. Resolve before commit.**

---

### 6. No Stale Pointers

**Check before commit:**
- Every `NEXT_TASK.md` reference exists
- Every `CURRENT_STATE.md` reference exists
- Every `ARCHITECTURE_FINGERPRINT.md` reference exists
- No references to deleted files
- No references to renamed files with old names

---

### 6. No Conflicting Milestone State

**Check before commit:**
- Only one milestone marked "CURRENT" or "IN_PROGRESS"
- No milestone marked both "COMPLETE" and "IN_PROGRESS"
- Roadmap sequence matches milestone numbering

---

### 7. No Conflicting Facts

**Check before commit:**
- Architecture status in `HERMES_ARCHITECTURE_STATE.md` matches `CURRENT_STATE.md`
- Test counts match across all documents
- Milestone status consistent across all documents
- Constitutional laws not duplicated with different numbers

---

## Validation Checklist (Run Before Every Commit)

- [ ] Single source of truth: No duplicate facts with different values
- [ ] No stale pointers: All references resolve
- [ ] Linear navigation: MANIFEST → SESSION → CURRENT_STATE → NEXT_TASK
- [ ] No stale pointers: All references resolve to existing files
- [ ] No conflicting milestone states
- [ ] No conflicting facts across documents
- [ ] Architecture fingerprint matches current architecture
- [ ] Engine contracts match domain models
- [ ] Constitutional laws not duplicated with different numbers
- [ ] Test counts consistent across all documents

---

## Validation Checklist for New AI

**Before starting work, verify:**

- [ ] Read MANIFEST.md
- [ ] Read SESSION.md
- [ ] Read CURRENT_STATE.md
- [ ] Read NEXT_TASK.md
- [ ] STOP (unless NEXT_TASK references another document)
- [ ] Verify no conflicts with current repository state
- [ ] Verify NEXT_TASK references existing documents

---

## Validation Checklist for Human Review

**Before merging PR:**

- [ ] All 7 validation rules pass
- [ ] No duplicate facts with conflicting values
- [ ] All pointers resolve
- [ ] Linear navigation preserved
- [ ] No stale pointers
- [ ] No conflicting facts
- [ ] Architecture fingerprint updated if architecture changed
- [ ] Engine contracts consistent with domain models
- [ ] Constitutional laws not duplicated with different numbers
- [ ] Test counts consistent
- [ ] Milestone status consistent
- [ ] No stale pointers

---

## Conflict Resolution Protocol

**If repository state conflicts with PMOS:**

1. **STOP.** Do not continue.
2. Document the conflict precisely.
3. Identify the authoritative source (PMOS single source of truth).
4. Fix the repository to match PMOS, or update PMOS if it was wrong.
5. Re-validate all 7 rules.
6. Only then continue.

**Never:** Guess, infer, assume, or continue with conflicts.