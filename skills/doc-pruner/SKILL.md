---
name: doc-pruner
description: Найти избыточную, пустую или устаревшую документацию и порекомендовать удаление/слияние.
---

# Documentation Pruner

Reduce documentation bloat without losing useful information. This skill only **recommends** — it never deletes files automatically.

## When to use

- After a big refactor that left stale docs behind.
- When `knowledge/` or `docs/` grows beyond ~150 files.
- Before a release cleanup.
- After `doc-audit` finds many stale/minor issues.

## Parameters

- `path` — project root (default: current directory).
- `threshold` — min file size in lines to flag as stub (default: 15).

## Checks

### 1. Duplicates

Find files with overlapping purpose:

- Same title / heading.
- Same content with minor formatting differences.
- Two docs explaining the same API/feature.

### 2. Stubs and placeholders

Flag files that are too short or empty:

- Files below `threshold` lines with no actionable info.
- Files containing only frontmatter and one sentence.
- Files with placeholders like `TODO`, `FIXME`, `WIP`, `TBD`.

### 3. Orphans

Find docs not linked from any INDEX:

- `.md` files in `docs/` or `knowledge/` with no backlink.
- Files not reachable via root `INDEX.md`, `docs/INDEX.md` or `knowledge/INDEX.md`.

### 4. Superseded knowledge

Use `Read` to find entries where:

- `status: superseded` but file still active in INDEX.
- `ended` date is set but content still appears in main body.
- Multiple entries describe the same bug/decision with different dates.

### 5. Over-documented areas

Find clusters where one small feature has >3 docs:

- Multiple guides for the same setup flow.
- Multiple architecture overviews.
- Excessive ADRs for trivial decisions.

## Output Format

```markdown
# Documentation Prune Report

## Safe to delete
| File | Reason | Suggested action |
|------|--------|------------------|
| `docs/old-setup.md` | Superseded by `docs/SETUP.md` | Delete |

## Merge into another file
| File | Target | Reason |
|------|--------|--------|
| `knowledge/bug-2025-x.md` | `knowledge/bugs.md` | Same bug, split unnecessarily |

## Mark as stale
| File | Reason |
|------|--------|
| `knowledge/pattern-v1.md` | Describes v1 API, now v2 |

## Keep
| File | Reason |
|------|--------|
| `docs/API.md` | Current, linked, valuable |

## Summary
- Files reviewed: [N]
- Recommended deletions: [N]
- Recommended merges: [N]
- Potential space saved: [N] lines
```

## Guardrails

- **Never delete files.** Only recommend.
- If a file is linked from `INDEX.md`, note it before recommending deletion.
- If removing a knowledge entry, suggest setting `status: superseded` and `ended` date instead of hard deletion.
- When in doubt, mark as `needs-human-review`.

**Результат сохранить в**: `.opencode/context/doc-prune-report.md`
