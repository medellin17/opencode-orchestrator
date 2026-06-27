---
name: skills-indexer
description: |
  Scans all available skills, maps them to agents in this project,
  and generates `.orchestrator/skills-index.md` + `skills-index.json`.
permission:
  read: allow
  write: allow
  edit: allow
  glob: allow
  grep: allow
  bash: allow
---

# Skills Indexer

## Purpose
Build a searchable, up-to-date index of ALL skills available to agents in this project:
- Local per-project skills (`.opencode/skills/`, `.gemini/skills/` in repo)
- Global opencode skills (`~/.config/opencode/skills/`)
- Global multi-agent skills (`~/.agents/skills/`)

And map each skill to the agent(s) and pipeline(s) that use it.

## When to run
- **At session start** — if `skills-index.md` is missing or older than 7 days.
- **After installing/removing a skill** — `npx skills add ...` or `rm -rf skills/...`.
- **On explicit request** — user says "rescan skills" or "update skills index".
- **After adding local project skills** under project root.

## Output files

| File | Purpose |
|------|---------|
| `.orchestrator/skills-index.md` | Human-readable table of all skills + agent mapping |
| `.orchestrator/skills-index.json` | Machine-readable index for conductor to load at runtime |

## Structure of skills-index.json

```json
{
  "generated_at": "2026-06-24T12:00:00Z",
  "sources_scanned": [
    {
      "path": ".opencode/skills/",
      "scope": "project",
      "skills": ["context-search", "plan-creator"]
    },
    {
      "path": "~/.config/opencode/skills/",
      "scope": "global",
      "skills": ["find-skills", "doc-coauthoring", "frontend-design"]
    }
  ],
  "skills": [
    {
      "name": "context-search",
      "description": "Retrieve ranked code context from SCR MCP server.",
      "location": ".opencode/skills/context-search/SKILL.md",
      "scope": "project",
      "suggested_agents": ["researcher-explorer", "architect-planner", "architect-planner-pro"],
      "tags": ["code", "search", "mcp"]
    }
  ]
}
```

## Execution Flow

To generate or update the skills index, run the Python script:

```bash
python3 ~/.config/opencode/skills/skills-indexer/scripts/generate_skills_index.py
```

Or copy the script directly if needed.

Do not attempt to implement parsing logic manually via shell commands. Use the script.

## Output on completion

The script output will summarize the result. Return a brief report based on that:

```
# Skills Index Report

- Project-local skills scanned: N
- Mapped to agents: N
- Unmapped skills: N

## Next steps
Conductor will load `.orchestrator/skills-index.json` to suggest relevant local skills to sub-agents during pipeline execution.
```
