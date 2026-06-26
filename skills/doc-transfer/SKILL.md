---
name: doc-transfer
description: Скопировать фреймворк документации и правил в целевой проект.
---

# Documentation Framework Transfer

The source framework root is provided by the Conductor as a parameter. If not provided, ask: 'Specify the source framework directory path.'

Install a complete documentation framework — AGENTS.md, rules, knowledge base, and supporting tooling — into another project.

## When to use

- Bootstrapping a new project with a documentation framework.
- Migrating an existing project to a structured agent-friendly workflow.
- Updating a downstream copy after framework changes.

## Parameters

- `target` — path to the target project root (required).
- `mode` — `full` (default) or `docs-only`. `docs-only` skips skills/runner scripts.
- `merge` — `true` (default): preserve existing files. `false`: overwrite.

## What gets transferred

### Full mode

From the source framework root into `target/`:

```text
AGENTS.md
README.md (renamed to FRAMEWORK-README.md if target README.md exists)
GUIDE.md
CYCLE.md
SKILLS-GUIDE.md
ORCHESTRATOR.md
profiles/
rules/
knowledge/
.agents/skills/*       # all skills
```

### Docs-only mode

```text
AGENTS.md
GUIDE.md
CYCLE.md
SKILLS-GUIDE.md
rules/
knowledge/
```

## Step 1. Detect conflicts

Before copying, check:

- Does `target/AGENTS.md` exist?
- Does `target/.agents/` exist?
- Does `target/rules/` or `target/knowledge/` exist?
- Does `target/orchestrate.py` or similar runner exist?

## Step 2. Merge or overwrite

If `merge=true`:

- `AGENTS.md` → append framework router sections, do not replace existing project identity.
- `rules/` → add missing framework rule files; do not touch existing rules.
- `knowledge/` → add missing framework knowledge files; keep existing entries.
- `.agents/skills/` → copy new skills; rename on conflict.

If `merge=false`:

- Backup existing `AGENTS.md` to `AGENTS.md.bak`.
- Copy framework files as-is.

## Step 3. Configure project identity

After transfer, prompt user to fill in `AGENTS.md` `# Project Identity`:

- Project type
- Language
- Stack
- Test/lint/build commands

## Step 4. Verify

Run `doc-audit` on the target to check the transfer result.

## Output Format

```markdown
# Documentation Transfer Report

- Target: [path]
- Mode: [full/docs-only]
- Merge: [true/false]
- Files copied: [N]
- Files merged: [N]
- Conflicts: [N]
- Next steps:
  1. Fill `# Project Identity` in AGENTS.md.
  2. Run `doc-scaffold` to tier-match docs.
  3. Run `doc-audit` to find gaps.
```

Write the transfer report to `.opencode/context/doc-transfer-report.md`.

## Guardrails

- Never delete the target project.
- If `target` is the framework repo itself, abort.
- Do not overwrite without backup when `merge=false`.
- Secrets (`.env`, keys) are never transferred.
