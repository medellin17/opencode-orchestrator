---
name: agentic-orchestrator
description: Universal multi-agent orchestration skill for OpenCode. Enables a primary conductor agent to decompose any complex task (software, content, data, design, research), select execution pipelines (sequential, parallel, conditional loops), dispatch work to specialized sub-agents, and synthesize final reports. Use when the user requests multi-step workflows, wants to run a team of agents, says "orchestrate this", "run agents", "use a pipeline", or needs plan-create-review cycles. Do NOT use for simple, single-file code modifications, straightforward bug fixes, minor edits, or basic questions.
---

# Agentic Orchestrator

This skill turns OpenCode into a universal multi-agent execution engine. A **primary conductor agent** (`orchestrator-conductor`) selects a pipeline, dispatches sub-agents via `task()`, and synthesizes the final result. Sub-agents never call each other directly — all routing goes through the conductor.

## How It Works

```
User Task (any domain)
    |
    v
Conductor (orchestrator-conductor)
    |---> researcher-explorer   (read-only investigation)
    |---> architect-planner     (design & strategy)
    |---> [conductor spot-check] (read/grep verification of key areas)
    |---> implementer-builder   (execution & creation)
    |---> [conductor spot-check] (read/grep verification of risk areas)
    |---> reviewer-critic       (audit & validation)
    |---> integrator-qa         (verification & testing)
    |---> content-writer        (writing & copywriting)
    |---> data-analyst          (analysis & processing)
    |---> debug                 (root-cause diagnostics)
    |---> code-reviewer         (structured code review)
    |---> test-engineer         (test generation)
    |---> security-auditor      (security scanning)
    |
    v
Final Synthesis Report
```

## Available Sub-Agents

| Agent | Role | Mode | Key Tools | Domains |
|-------|------|------|-----------|---------|
| `orchestrator-conductor` | **Primary conductor.** Plans, delegates, spot-checks, synthesizes. | primary | `task`, `skill`, `read`, `grep` | All |
| `researcher-explorer` | **Read-only exploration.** Maps code, data, content. | subagent | `read`, `grep`, `glob`, `webfetch` | All |
| `architect-planner` | **Design & strategy.** Writes specs, no implementation. | subagent | `read`, `grep` (read-only) | Software, Systems, Content |
| `implementer-builder` | **Execution specialist.** Writes code, configs, scripts. | subagent | `read`, `edit`, `write`, `bash` | Software, Engineering |
| `reviewer-critic` | **Audit & review.** Checks correctness, quality, compliance. | subagent | `read`, `grep` (read-only) | All |
| `integrator-qa` | **Verification.** Runs tests, validates alignment. | subagent | `read`, `bash` | Software, Data |
| `content-writer` | **Writing & copywriting.** Produces text content. | subagent | `read`, `write`, `edit` | Content, Marketing, Docs |
| `data-analyst` | **Analysis & processing.** Cleans, analyzes, visualizes. | subagent | `read`, `write`, `bash` | Data, Research, Business |
| `ux-designer` | **UX researcher & designer.** User flows, wireframes, interactions. | subagent | `read`, `write`, `edit` | Design, Product, Content |
| `debug` | **Diagnostics.** Finds root causes. | subagent | `read`, `edit`, `write`, `bash` | Software |
| `code-reviewer` | **Structured code review.** 5-dimension evaluation. | subagent | `read`, `grep` | Software |
| `test-engineer` | **Test generation.** Creates test suites. | subagent | `read`, `write`, `edit`, `bash` | Software |
| `security-auditor` | **Security scanning.** Finds vulnerabilities. | subagent | `read`, `grep`, `bash` | Software, Systems |
| `skills-indexer` | **Skills discovery.** Scans and maps all available skills to agents. | subagent | `read`, `write`, `glob`, `bash` | All |
| `doc-maintainer` | **Documentation maintainer.** Updates project docs (AGENTS.md, knowledge/, rules/) after changes. | subagent | `read`, `write`, `edit`, `glob`, `bash` | All |

## Skills Discovery & Agent Mapping

In addition to the built-in sub-agents, OpenCode supports **skills** (instruction modules) that extend agent capabilities. Skills live in three layers:
- **Project-local**: `.opencode/skills/`, `.gemini/skills/` under the working directory.
- **Global (OpenCode)**: `~/.config/opencode/skills/`
- **Global (multi-agent)**: `~/.agents/skills/`

The `skills-indexer` agent generates an index of all discovered skills and maps each to the agent(s) best suited to use it.

### Generated index files

| File | Format | Purpose |
|------|--------|---------|
| `.orchestrator/skills-index.md` | Markdown | Human-readable table of all skills, their descriptions, locations, and suggested agents. |
| `.orchestrator/skills-index.json` | JSON | Machine-readable index. Conductor can load this at runtime to find skills matching a task domain. |

Both files are **auto-generated** and should not be manually edited. Re-run `skills-indexer` when skills are added, removed, or renamed.

### Loading index at runtime

Conductor should check for `.orchestrator/skills-index.md` at the start of each execution:
- If missing or > 7 days old → dispatch `skills-indexer` to regenerate it.
- Then scan `skills-index.md` for skills whose tags match the current task domain.
- Include the skill name(s) in sub-agent prompts so they know which skill to follow.

Example: updating architecture docs → scan `skills-index.md` → find `architecture-update` skill → dispatch `architect-planner` with instruction to follow `architecture-update` skill.

### Registering a new skill

When a new skill is created (local or global):
1. Add the `SKILL.md` to the appropriate `skills/` directory.
2. Re-run `skills-indexer` to regenerate indices.
3. Node any agent that should explicitly reference the skill in its prompt.
4. Conductor can now route tasks that match the skill's domain to the appropriate agent.

## Predefined Pipelines

### Core Pipelines (Domain-Agnostic)

All pipelines below work for **any domain**. Sub-agents adapt their output format to the task at hand.

#### 1. `research` — Pure Discovery
```
researcher-explorer
```
**Use when**: Need to understand existing state before action.
**Output**: Structured findings report.
**Works for**: Codebases, datasets, documents, markets, competitors.

#### 2. `plan` — Strategy Before Execution
```
researcher-explorer  →  architect-planner
```
**Use when**: Need a structured approach before building/writing.
**Output**: Technical spec, content outline, analysis plan.

#### 3. `plan-review` — Validated Strategy
```
researcher-explorer  →  architect-planner  →  reviewer-critic
```
**Use when**: High-stakes plan that must be critiqued before execution.

#### 4. `build` — Straightforward Execution
```
researcher-explorer  →  architect-planner  →  implementer-builder  →  [conductor spot-check]  →  integrator-qa
```
**Use when**: Clear spec, low risk. Collects context first, plans, then executes.
Conductor spot-checks the implementation before final QA.

#### 5. `build-review` — Standard Robust Pipeline
```
researcher-explorer  →  architect-planner  →  [conductor spot-check]  →  reviewer-critic
                      →  implementer-builder  →  [conductor spot-check]  →  reviewer-critic  →  integrator-qa
```
**Use when**: Standard quality bar. Most common pipeline.
Conductor spot-checks after architect (plan) and after implementer (code) before each review.

#### 6. `debug-fix` — Troubleshooting
```
researcher-explorer  →  architect-planner  →  debug  →  implementer-builder  →  integrator-qa
```
**Use when**: Something is broken. Explores context, builds a reproduction/fix plan, runs debug tool, writes code.

#### 7. `parallel-audit` — Multi-Dimensional Review
```
reviewer-critic  ∥  security-auditor  →  synthesize
```
**Use when**: Auditing from multiple angles simultaneously.

#### 8. `full-cycle` — Mission-Critical Task
```
researcher-explorer  →  architect-planner  →  [conductor spot-check]  →  reviewer-critic
                      →  implementer-builder  →  [conductor spot-check]  →  reviewer-critic
                      →  integrator-qa  →  doc-maintainer
```
**Use when**: Complex, high-impact work where every phase needs validation, and docs must be updated.
Conductor spot-checks after both architect and implementer before each review.

#### 9. Auto-Documentation Modifier
```
Append `→ doc-maintainer` to the end of **any** pipeline above (e.g., `build-review → doc-maintainer`).
```
**Use when**: The task modifies architecture, adds APIs, or introduces new patterns that should be recorded in the project's `knowledge/` directory. Pass the execution summary to the `doc-maintainer` agent.

### Domain-Specific Pipeline Examples

| Domain | Task Example | Pipeline | Agents Used |
|--------|-------------|----------|-------------|
| **Software** | "Add OAuth2 to FastAPI app" | `full-cycle` or `build-review` | researcher, architect, builder, reviewer, QA |
| **Content** | "Write technical blog post about API" | `plan` → `content-writer` → `reviewer-critic` | researcher, architect (outline), writer, reviewer |
| **Data** | "Analyze Q3 sales data" | `research` → `data-analyst` → `reviewer-critic` | explorer, analyst, reviewer |
| **Research** | "Compare 3 competing products" | `research` → `data-analyst` → `reviewer-critic` | explorer, analyst, reviewer |
| **Marketing** | "Create landing page copy" | `plan` → `content-writer` → `reviewer-critic` → `integrator-qa` | architect (brief), writer, reviewer, QA (A/B test plan) |
| **Docs** | "Write API documentation" | `research` → `content-writer` → `reviewer-critic` | explorer, writer, reviewer |
| **Design** | "Design onboarding flow for new users" | `research` → `ux-designer` → `reviewer-critic` → `implementer-builder` | explorer, designer, reviewer, builder (prototype) |

## Dispatch Protocol

### Calling a Sub-Agent

Use OpenCode's `task()` tool. The conductor agent has permissions to call all sub-agents.

```
task({
  description: "Short task label",
  prompt: "You are [agent-role].\n\nGoal: [what to accomplish]\n\nDomain: [software/content/data/design/etc]\n\nContext:\n[You MUST provide clear, necessary context strictly needed for this task: no more, no less. Include the original request context, the current plan, and details of prior changes (files, lines, purpose). You MUST copy-paste the exact outputs, research details, and drafts from previous sub-agents here. DO NOT reference external state or say 'based on research' without pasting that research here. Sub-agents have no shared memory!]\n\nDeliverable: [expected output format]\n\nConstraints:\n[what NOT to do, quality standards]\n\nReturn your results in the format defined in your agent instructions.",
  command: "Optional command to verify",
  subagent_type: "[agent_type_name]"
})
```

For verification, review, and QA steps:
- You MUST give the verifying agent clear context on what was changed, why, and which files/sections are affected. Do not ask to verify lines in a vacuum; provide the goal of those changes so the agent can assess correctness.

### Passing Context Between Steps

Always copy-paste the relevant user request context, the active plan, and the previous sub-agent's exact output (research, draft, specs) into the next `task()` call under a `## Previous Context` section. This preserves continuity without relying on shared memory. Do not summarize or reference them abstractly.

### Handling Parallel Execution

Launch independent `task()` calls in the same response. Collect all results before proceeding to dependent steps.

### Handling Conditional Loops

If a reviewer rejects a plan or QA fails:
1. **Capture the feedback** verbatim.
2. **Route back** to the appropriate upstream agent.
3. **Include the feedback** as context.
4. **Set a retry limit** — max 3 iterations before escalating to the user.

## Synthesis Report Template

After the pipeline completes, the conductor produces:

```markdown
## Execution Summary

**Pipeline Used**: [name]
**Status**: Complete / Partial / Failed

### What Was Done
[Stage-by-stage summary]

### Key Decisions
[Important choices and trade-offs]

### Deliverables
[What was produced — files, plans, reports, code, content]

### Verification
[How quality was ensured]

### Issues & Next Steps
[Unresolved items and recommendations]
```

## Rules for Conductors

1. **Never execute work yourself.** Always delegate to specialized sub-agents.
2. **Spot-check before full review.** After key sub-agent outputs (implementer, architect), use your `read`/`grep` access to verify critical areas. If you find issues — dispatch implementer to fix directly. Only dispatch `reviewer-critic` for comprehensive review.
3. **Full review via sub-agents.** For security audits, deep code review, or QA — still use `reviewer-critic` or `integrator-qa`. Spot-check is for fast verification, not a replacement.
4. **No direct exploration.** Conductor must NOT read files for exploration or context-gathering. Always dispatch `researcher-explorer` for that. Read access is ONLY for verification of sub-agent work.
5. **Adaptive Granularity — Split More, Not Less:**
   - Default to fine-grained decomposition: one agent per phase (research, plan, implement, review), one agent per domain.
   - Merge steps ONLY for trivial tasks (1 file, <30 lines, no new patterns).
   - When in doubt, split. Extra roundtrips cost tokens, but a single overloaded agent costs quality.
   - You can split implementation across multiple `implementer-builder` calls — one per logical unit (e.g., core flow, then tests, then edge cases).
6. **Always announce the chosen pipeline** at the start of execution.
7. **Preserve full context.** When calling sub-agents, you MUST pass all required artifact contents, files, research data, and text blocks directly inside the `Context:` block of the `task()` tool call. Sub-agents run in fresh sessions and cannot see variables, terminal outputs, or state from other agents unless you explicitly print or write them into the prompt's Context. Never give prompts like "critique the drafted text" without providing the actual drafted text in the prompt. If you ask an agent to review, edit, or critique a draft, code snippet, or description, you MUST copy-paste the exact target text/code/research directly into the prompt.
8. **Never reference external state implicitly.** You are strictly forbidden from assuming the sub-agent has access to "the previous draft" or "the site details" or "the research" without you providing them in the task payload. You must copy-paste the exact text and results from the previous step.
9. **Respect retry limits.** After 3 failed iterations, escalate to user.
10. **Synthesize, don't dump.** Final report must be concise and actionable.
11. **AGENTS.md (Project Context) Awareness:** Instruct sub-agents to look for `AGENTS.md` (or instructions from it in ~/.config/opencode/AGENTS.md) to load project-specific commands, style guides, and workflows. This promotes just-in-time context loading and avoids token bloat.
