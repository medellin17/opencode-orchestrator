---
name: architecture-update
description: Безопасно обновить knowledge/architecture.md.
---

# Architecture Update

Purpose: Keep `knowledge/architecture.md` in sync with the codebase without data races, deadlocks, or corrupting the Mermaid diagrams.

## When to use

- After a refactor that changes module relationships.
- After `dependency-auditor` revealed new callers or dependencies.
- When `doc-update` identifies that architecture docs are stale.
- When generating the initial architecture diagram for a new project.

## Inputs

- `project_root` — absolute path to the project.
- `patch_file` — path to a markdown file containing the new `architecture.md` content.
- `expected_head_hash` — optional Git HEAD hash captured during the audit that justifies the update.

## Workflow

1. **Prepare the patch content.**
   Ensure the patch includes balanced Mermaid markers:
   ```markdown
   <!-- mermaid:start -->
   graph TD
       A --> B
   <!-- mermaid:end -->
   ```
   If the existing `architecture.md` has no markers, the patch should introduce them.

2. **Check Git status (optional but recommended).**
   Validate that the working tree is clean outside `knowledge/`, `.tmp/`, and `.gitignore` paths. If the current task legitimately changed code, capture the HEAD hash before the audit and pass it as `expected_head_hash`, or skip the check only when you are certain the changes belong to the current task.

3. **Apply the patch.**
   If your project has an architecture-update helper script, use it. Otherwise, use direct file Write/Edit to update `knowledge/architecture.md`.
   Read the current `architecture.md` with Read tool, apply your patch using Edit, and verify the Mermaid markers are balanced.

4. **Verify the result.**
   Confirm the file was updated and no stray `.bak` or `.lock` files remain.

## Guardrails

- Use an atomic write pattern: `architecture.md.tmp` → OS-level rename → `architecture.md`. Keep a `.bak` copy until the rename succeeds.
- If Git status validation fails, block the update to prevent overwriting docs based on an outdated audit.
- Mermaid markers must be balanced; otherwise the update is rejected.
- Never delete `knowledge/architecture.md.lock` while another process may be running it.

## Output

Return:
- Path to the updated `architecture.md`.
- Whether Git status validation was skipped.
- Any warnings about recovery from a previous crash.

Save any auxiliary files to `.opencode/context/architecture-update/`
