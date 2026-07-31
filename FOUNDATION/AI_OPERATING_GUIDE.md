# AI Operating Guide

## How to Operate Hermes

### Startup Sequence (Mandatory)

Every AI session must follow this exact sequence:

1. **Read MANIFEST.md** — Entry point
2. **Read SESSION.md** — Current session context
3. **Read CURRENT_STATE.md** — Current project truth
4. **Read NEXT_TASK.md** — Exactly one approved implementation target

**STOP.** Only continue if NEXT_TASK references another document.

---

## Operating Rules

### Token Optimization
- Read only what's necessary
- Never read entire repository
- Follow pointer chain: MANIFEST → SESSION → CURRENT_STATE → NEXT_TASK
- Only load referenced documents

### Anti-Hallucination Protocol
If repository state conflicts with PMOS:
1. **STOP**
2. **Never guess**
3. **Never infer**
4. **Never continue**
5. **Explain conflict**

### Duplicate Prevention
Before ANY implementation:
1. Check CURRENT_STATE — already implemented?
2. Check reports/ — already verified?
3. Check docs/ — already documented?
4. Check approvals — already approved?

If YES to any: **STOP.**

### Single Source of Truth
| Fact | Single Owner |
|------|--------------|
| Current milestone | CURRENT_STATE only |
| Next implementation | NEXT_TASK only |
| Architecture | architecture/ only |
| Reports | reports/ only |
| Roadmap | ROADMAP only |
| Decisions | ADRs only |

Never duplicate facts across documents.

---

## Session Protocol

### Starting a Session
1. Read MANIFEST.md
2. Read SESSION.md
3. Read CURRENT_STATE.md
5. Read NEXT_TASK.md
6. **STOP** unless NEXT_TASK references another document

### During Session
- Follow NEXT_TASK exactly
- Update SESSION.md with decisions
- Update CURRENT_STATE.md with changes
- Never modify architecture without constitutional amendment

### Ending a Session
1. Update SESSION.md with log
2. Update CURRENT_STATE.md if changed
3. Update NEXT_TASK if changed
3. Commit with descriptive message
4. Push to origin

---

## Forbidden Actions

| Action | Reason |
|--------|--------|
| Read entire repository | Token waste, hallucination risk |
| Guess architecture | Constitution is explicit |
| Skip PMOS steps | Violates operating protocol |
| Modify domain without amendment | Constitution is supreme |
| Duplicate facts across docs | Single source of truth |
| Guess when uncertain | Anti-hallucination protocol |

---

## Conflict Resolution

If PMOS state conflicts with repository:

1. **STOP immediately**
2. Document the conflict explicitly
3. Do not proceed
4. Request human resolution

Never guess. Never infer. Never continue.