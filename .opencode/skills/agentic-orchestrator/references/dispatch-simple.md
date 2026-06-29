# Dispatch Template: Simple / General

This reference shows how the conductor should write `task()` prompts for sub-agents
in the common case. Sub-agents run on **weaker models** — they need more explanation,
structure, and explicit constraints than you (the conductor on a pro model).

## The task() Call

```
task({
  description: "What this sub-agent does (3-7 words)",
  prompt: "[FULL PROMPT — see structure below]",
  subagent_type: "agent-type-name"
})
```

## Prompt Structure

Every sub-agent prompt must have these sections:

```
You are [agent-role]. You have a specific task to complete and MUST return results.

## Goal
[One sentence: what to produce. Be concrete: "write a plan for OAuth2 integration"
not "help with auth".]

## Context
[Copy-paste relevant artifacts from previous steps HERE — the sub-agent has no memory.
Include: user's original request, plan from architect-planner, files/lines changed
by implementer-builder, research findings from researcher-explorer.
NEVER say "based on the plan above" — paste the plan IN THIS SECTION.]

## Deliverable
[Exact output: "a markdown report saved to data/tasks/foo/report.md" or
"a diff applying the change to src/auth.py". Be specific about FORMAT and LOCATION.]

## Constraints
- What NOT to do
- Files/directories to avoid
- Size/scope limits
- [domain-specific constraints]

## Verification Hints (for implementer-builder and architect-planner)
[Optional but recommended. The reviewer uses these for targeted verification.]
- risk_areas: [specific lines/methods where you improvised or are uncertain]
- confidence: [high / medium / low]
- needs_deep_check: [true if this needs reviewer-critic-pro instead of reviewer-critic]
```

## Weak Model Mindset

Your sub-agents run on a weaker model (mimo-v2.5). You run on pro. This means:

- **Over-explain.** Don't assume the sub-agent will "figure it out." Spell out edge cases.
- **One task per dispatch.** Don't ask a sub-agent to "research the codebase AND write a plan
  AND implement." Each agent does ONE thing.
- **Checklists help.** If the task has 3+ steps, include a numbered checklist so the
  sub-agent doesn't skip steps.
- **Anticipate confusion.** Pre-emptively address where the sub-agent might go wrong:
  "Don't confuse X with Y. X is in file A, Y is in file B."
- **Validate format explicitly.** If you need JSON, say "Output ONLY valid JSON, no markdown
  wrapper, no explanation." If you need file paths, say "Output file paths as absolute paths
  in a bullet list."
- **Less context is sometimes more.** Give the sub-agent exactly what it needs — no extra.
  A 2000-line code dump will overwhelm a weaker model. Extract the relevant 50 lines.
- **Request verification hints.** When dispatching implementer-builder or architect-planner,
  explicitly ask for `risk_areas` and `confidence` in the deliverable. This helps the
  reviewer focus on the riskiest parts instead of reading the entire codebase.

## Good vs Bad Dispatch

### BAD (vague, no context, assumed shared memory):
```
task({
  description: "Review the plan",
  prompt: "You are a reviewer. Review the plan and tell me what's wrong.",
  subagent_type: "reviewer-critic"
})
```

### GOOD (concrete, context inline, explicit deliverable):
```
task({
  description: "Review OAuth2 architecture plan",
  prompt: `You are reviewer-critic. Review the following architecture plan for
correctness, security gaps, and feasibility.

## Goal
Critique the OAuth2 integration plan. Identify risks, missing edge cases,
and over-engineering. Return a structured review.

## Context
[User request]: Add OAuth2 (Google + GitHub) to the FastAPI backend.
Plan from architect-planner:
--- PLAN START ---
[copy-paste the full plan here]
--- PLAN END ---
Existing auth stack: currently uses JWT with bcrypt, no OAuth support.
Affected files: src/auth.py (current auth), src/config.py (settings).

## Deliverable
A markdown report in this structure:
1. Summary (2-3 sentences)
2. Critical issues (blockers)
3. Risks (non-blocking)
4. Missing edge cases
5. Verdict: APPROVED / NEEDS REVISION / REJECT
Save to data/tasks/oauth/review.md.

## Constraints
- Do NOT edit any files. Read-only.
- Focus on ARCHITECTURE, not code style.
- Assume the team knows Python and FastAPI.`,
  subagent_type: "reviewer-critic"
})
```

### GOOD (implementer dispatch with verification hints):
```
task({
  description: "Implement OAuth2 endpoints",
  prompt: `You are implementer-builder. Implement the OAuth2 endpoints per the plan below.

## Goal
Create src/auth/oauth.py with Google + GitHub OAuth2 flows, and tests.

## Context
[User request]: Add OAuth2 (Google + GitHub) to the FastAPI backend.
Plan:
--- PLAN START ---
[copy-paste the full plan here]
--- PLAN END ---
Existing auth stack: src/auth.py uses JWT with bcrypt.

## Deliverable
Implementation report in this format:
1. Files Created/Modified
2. Tests Added
3. Verification (commands run)
4. Deviations from Plan
5. Risk Areas — specific lines where you improvised or are uncertain
6. Confidence — high/medium/low with 1-sentence explanation

Save to data/tasks/oauth/implementation.md.

## Constraints
- Follow the plan exactly. If ambiguous, ask.
- Match existing code style.
- Run tests and report results.
- Include Risk Areas and Confidence honestly — the reviewer will verify flagged lines.`,
  subagent_type: "implementer-builder"
})
```
