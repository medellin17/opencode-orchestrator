---
name: doc-update
description: Предложить обновления документации после изменений кода.
---

# Documentation Update

After changing code, find the docs that need updating and propose concrete edits.

## When to use

- After implementing a feature.
- After adding/changing an API endpoint.
- After renaming a field, function, or route.
- After fixing a bug that should be recorded.
- After `doc-audit` flags consistency issues.

## Parameters

- `changes` — description of what changed, diff, or list of modified files.
- `scope` — `all` (default), `api`, `guides`, `knowledge`, `changelog`.

## Step 1. Understand the change

From the input, identify:

- New/updated/deleted endpoints.
- New/renamed functions, classes, modules.
- New environment variables or config.
- New dependencies or build steps.
- Behavior changes visible to users.
- Bug fixes worth recording.

## Step 2. Find affected docs

Use `Glob`, `Grep`, and `Read`:

- API changes → `docs/API.md`, `knowledge/api.md`.
- Architecture changes → `knowledge/architecture.md`, `docs/ARCH.md`.
- User-facing changes → `README.md`, guides in `docs/`.
- Bug fixes → `knowledge/bugs.md`.
- Decisions → `knowledge/decisions.md`.
- Releases → `knowledge/changelog.md`, `CHANGELOG.md`.

## Step 3. Propose edits

For each affected doc, produce:

```markdown
### `docs/API.md`
- Add new endpoint `/tasks/bulk`.
- Update request schema for `/users` (added `theme_preference`).
- Suggested diff: ...
```

For `knowledge/architecture.md`, never edit the file directly. Instead:

1. Prepare a full patch file that preserves existing Mermaid markers (`<!-- mermaid:start -->` / `<!-- mermaid:end -->`).
2. Run `skill({ name: "architecture-update" })` for architecture.md changes.

Use `Edit` to apply changes only after user confirmation.

## Step 4. Record new knowledge

For findings that future agents should remember, write directly to knowledge files with `Write`/`Edit`:

- New API quirk → `knowledge/patterns.md`.
- Bug fix → `knowledge/bugs.md`.
- Architectural decision → `knowledge/decisions.md`.
- Release note → `knowledge/changelog.md`.

## Output Format

```markdown
# Documentation Update Proposal

## Summary
- Changed files: [list]
- Docs affected: [N]
- New knowledge entries: [N]

## Proposed edits
1. `docs/API.md` — add `/tasks/bulk`
2. `knowledge/changelog.md` — record feature
3. `README.md` — update setup command

## Knowledge to record
- decision: [why bulk endpoint uses POST not PUT]
- api: [bulk endpoint pagination limit]

## Next step
Confirm edits and run `doc-audit`.
```

## Guardrails

- Do not change docs that are unrelated to the code change.
- If a doc is large, prefer targeted `Edit` over full rewrite.
- If user says no, do not apply edits.
- Keep changelog entries concise: what, when, why.

**Результат сохранить в**: `.opencode/context/doc-update-report.md`
