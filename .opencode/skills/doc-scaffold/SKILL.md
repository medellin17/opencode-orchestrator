---
name: doc-scaffold
description: Оценить размер проекта и создать подходящий каркас документации.
---

# Documentation Scaffold

Create or extend project documentation based on its size and complexity.

## When to use

- Starting a new project.
- Bootstrapping docs in an existing project.
- After significant growth — upgrading documentation tier.
- Before handing a project to another agent/team.

## Parameters

- `path` — project root (default: current working directory).
- `tier` — force tier: `S`, `M`, `L`, `XL`. If omitted, auto-detect and ask.
- `merge` — `true` (default): preserve existing files and append missing pieces. `false`: create fresh scaffold (dangerous).

## Tier Definitions

| Tier | Code LOC | Modules | Docs |
|------|----------|---------|------|
| **S** | < 2 000 | 1 | `AGENTS.md`, `README.md`, `knowledge/` (6 files), `rules/` (3 files) |
| **M** | 2 000 – 15 000 | 2–3 | S + `INDEX.md`, module `AGENTS.md`, `knowledge/` + `deployment.md`, `security.md` |
| **L** | 15 000 – 50 000 | 3–6 | M + per-module `rules/`, `knowledge/<module>/`, `docs/INDEX.md`, `docs/API.md`, `docs/ARCH.md`, `docs/SMOKE-CHECKLIST.md` |
| **XL** | > 50 000 | 6+ | L + `docs/ai-maintainability/AGENTS.md`, `knowledge/INDEX.md`, nested module memory, frontmatter in every entry |

Module = independently deployable part: `bot/`, `web/backend/`, `web/frontend/`, `web/shared/`, `mobile/`, `scripts/`, etc.

## Step 1. Auto-detect project size

Exclude from counting: `.git/`, `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `.opencode/`, `.agents/`, vendored/generated assets.

1. Count code lines per language: `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.go`, `*.rs`, etc.
2. Count top-level module directories.
3. Propose tier based on the table above.
4. Ask user: `Proposed tier: X. Confirm or override?`

## Step 2. Detect existing docs

Search for existing files:
- `AGENTS.md`, `README.md`, `INDEX.md`
- `docs/**/*.md`
- `knowledge/**/*.md`
- `rules/**/*.md`

Use `Read` to inspect current knowledge entries.

## Step 3. Create/extend files

For each tier, ensure these files exist. If `merge=true`, append missing sections instead of overwriting.

### Tier S

- `AGENTS.md` — project identity, quick reference, router, core constraints, memory list, compaction rules.
- `README.md` — what, why, quick start, stack.
- `knowledge/decisions.md` — architectural decisions.
- `knowledge/bugs.md` — bugs: symptom → root cause → fix.
- `knowledge/patterns.md` — API quirks, patterns, gotchas.
- `knowledge/api.md` — endpoints/contracts.
- `knowledge/architecture.md` — components/layers.
- `knowledge/changelog.md` — what changed, when, why.
- `rules/coding.md` — coding rules.
- `rules/testing.md` — testing rules.
- `rules/architecture.md` — architecture rules.

### Tier M

All of S, plus:
- `INDEX.md` — map of all project docs.
- `{module}/AGENTS.md` for each detected module.
- `knowledge/deployment.md` — deployment notes.
- `knowledge/security.md` — security lessons.

### Tier L

All of M, plus:
- `{module}/rules/coding.md`, `{module}/rules/testing.md` per module.
- `knowledge/{module}/` subfolder per module with its own decisions/bugs/patterns.
- `docs/INDEX.md` — map of files inside `docs/`.
- `docs/API.md` — public API reference.
- `docs/ARCH.md` — architecture overview.
- `docs/SMOKE-CHECKLIST.md` — post-change checks.

### Tier XL

All of L, plus:
- `docs/ai-maintainability/AGENTS.md` — agent router for AI maintainability docs; links to contracts, playbooks and hotspots.
- `knowledge/INDEX.md` — searchable index of all knowledge files with backlinks.
- YAML frontmatter on every knowledge entry (`confidence`, `status`, `last_verified`, `source`).
- `docs/decisions.md` or `docs/adr/` for formal ADRs.

## Step 4. Write and confirm

Use `Write` and `Edit` for AGENTS.md, README.md, docs, rules, and knowledge files. Use direct file operations (Write/Edit/Read) for all documentation work.

After creating, output:
```markdown
# Documentation Scaffold Report

- Proposed tier: [S/M/L/XL]
- Confirmed tier: [S/M/L/XL]
- Files created: [N]
- Files extended: [N]
- Existing files preserved: [N]
- Next step: run `doc-audit` to find gaps.
```

## Guardrails

- Never overwrite existing content without marking it with `<!-- SCAFFOLD: review below -->`.
- If `merge=true` and file exists, append missing sections rather than replacing.
- Do not delete existing docs.
- Keep scaffold minimal: only create files required for the tier.
