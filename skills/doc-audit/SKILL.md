---
name: doc-audit
description: Аудит состояния документации и её соответствия коду.
---

# Documentation Audit

Check that project documentation is correct, complete, and up-to-date.

## When to use

- Before release.
- After refactoring or API changes.
- When onboarding a new agent/team member.
- When docs feel stale or contradictory.
- After running `doc-scaffold` to verify gaps were filled.

## Parameters

- `scope` — `all` (default), `structure`, `completeness`, `freshness`, `consistency`, `contradictions`.
- `path` — project root (default: current directory).

## Pass A. Structure

Check that the documentation skeleton is sound:

1. Does `AGENTS.md` exist? Is it ≤ 120 lines and router-first?
2. Does `README.md` exist?
3. Does `knowledge/` exist with the expected files for the project's tier?
4. Does root `INDEX.md`, `docs/INDEX.md` or `knowledge/INDEX.md` exist (M+ / XL)?
5. Are there orphan `.md` files not linked from any INDEX?
6. Are module `AGENTS.md` files present where expected?

## Pass B. Completeness

Find missing or empty documentation:

1. Blank placeholders: files < 15 lines with no actionable info.
2. Missing API docs when API routes/endpoints exist in code.
3. Missing architecture docs for non-trivial systems.
4. Missing module docs for detected modules.
5. Missing changelog entries for recent changes.
6. Missing security/deployment notes for production projects.

## Pass C. Freshness

Detect stale information:

1. Knowledge entries with `last_verified` > 30 days ago and `status: active`.
2. Docs referencing removed files, functions, or endpoints.
3. Outdated screenshots, GIFs, or videos in guides.
4. Dates in changelog not matching git tags/releases.
5. TODOs/FIXMEs in code not reflected in docs.

Use `Read` to sample knowledge files and check dates/frontmatter.

## Pass D. Code Consistency

Verify docs match the actual code:

### README
- Project description matches current behavior.
- Install/run commands still work.
- Stack list matches `package.json`, `pyproject.toml`, `requirements.txt`.

### API docs
- Every documented endpoint exists in code.
- Every endpoint in code is documented.
- Request/response parameters match schemas.
- Status codes match implementation.

### Guides
- UI elements mentioned in guides exist in code.
- Steps match current flow.
- Examples are runnable.

### Changelog
- Latest version matches latest git tag / release.
- Breaking changes are described.

## Pass E. Contradictions

Find conflicting statements:

1. Two docs say opposite things about the same behavior.
2. A doc says X but code says Y.
3. `knowledge/decisions.md` contradicts current architecture.
4. Module `AGENTS.md` contradicts root `AGENTS.md`.
5. Frontmatter `status: active` vs body saying something is deprecated.

Use `Read` and `Grep` across knowledge files to find conflicting claims.

## Pass F. Architecture Consistency Check

Verify that `knowledge/architecture.md` matches the actual codebase:

1. Extract Mermaid diagrams and the modules/names they reference.
2. For each important symbol/path mentioned, check that it exists in the code.
3. Flag symbols or files in the diagram that no longer exist, were renamed, or are missing from the code.
4. Flag major dependencies in the code that are absent from the diagram.
5. Write findings to a temporary report in `.tmp/doc-audit-report-*.md` without modifying `architecture.md`.

This pass is strictly read-only.

## Output Format

Produce one findings table:

```markdown
| Severity | Pass | File | Issue | Evidence | Suggested Fix |
|----------|------|------|-------|----------|---------------|
| Critical | D | docs/API.md | Endpoint /users/{id} not in code | routes.py has no /users/{id} | Remove or find correct route |
| Major | C | knowledge/bugs.md | last_verified 2026-01-01, status active | 5 months old | Re-verify and update date |
| Minor | B | docs/guides/setup.md | Blank placeholder | 8 lines total | Fill or delete |
```

Severity:
- **Critical** — doc is wrong and will mislead implementation/deploy.
- **Major** — important gap or stale info.
- **Minor** — cosmetic, missing link, formatting.

## Final Report

```markdown
# Documentation Audit Report

- Files checked: [N]
- Critical: [N]
- Major: [N]
- Minor: [N]
- Top fixes:
  1. ...
  2. ...
- Next step: run `doc-update` for code changes or `doc-pruner` for cleanup.
```

## Record

If audit reveals an architectural decision that caused doc drift, record it in `knowledge/decisions.md` via direct `Write`/`Edit`.
