# Dispatch Template: Parallel Execution

Use this template when launching multiple independent sub-agents simultaneously.
Parallel dispatch saves wall-clock time and improves coverage on multi-faceted tasks,
especially when agents run on cheap models.

## When to Parallelize

**Parallelize when agents are independent:**
- Multiple reviewers inspecting the same artifact from different angles.
- Multiple researchers exploring different facets of a problem.
- Multiple implementers working on clearly separate modules after the plan is locked.

**Never parallelize:**
- `architect-planner-pro` with anything else. Complex planning must be sequential.
- Any agent whose output is another agent's input in the same stage.
- Ordered phases (research → plan → implement → review).

**Cost rule:** Parallelize cheap (mimo-v2.5) agents by default. Be selective with
parallel pro-model calls.

## How to Dispatch in Parallel

Launch independent `task()` calls in the same response. Each agent gets the same
base context but a different angle in the Goal/Constraints. Collect all results
before synthesizing.

## Example: Parallel Review

```
task({
  description: "Review OAuth2 plan for correctness",
  prompt: `You are reviewer-critic. Review the following OAuth2 architecture plan
for correctness, feasibility, and missing edge cases.

## Goal
Identify functional gaps and risks in the OAuth2 plan.

## Context
[User request]: Add OAuth2 (Google + GitHub) to the FastAPI backend.
Plan:
--- PLAN START ---
[copy-paste the full plan here]
--- PLAN END ---

## Deliverable
A structured review with Critical issues, Risks, Missing edge cases, and Verdict.
Save to data/tasks/oauth/review-correctness.md.

## Constraints
- Focus on correctness and feasibility, not style.
- Do NOT edit files.`,
  subagent_type: "reviewer-critic"
})

task({
  description: "Review OAuth2 plan for security",
  prompt: `You are security-auditor. Review the following OAuth2 architecture plan
for security vulnerabilities and OWASP compliance.

## Goal
Identify security gaps in the OAuth2 plan.

## Context
[User request]: Add OAuth2 (Google + GitHub) to the FastAPI backend.
Plan:
--- PLAN START ---
[copy-paste the full plan here]
--- PLAN END ---

## Deliverable
A security review with Threats, Vulnerabilities, Mitigations, and Verdict.
Save to data/tasks/oauth/review-security.md.

## Constraints
- Focus on security only.
- Do NOT edit files.`,
  subagent_type: "security-auditor"
})
```

## After Parallel Agents Return

1. Read all outputs.
2. Reconcile conflicts explicitly (do not ignore contradictions).
3. Produce a single synthesized artifact.
4. Pass the synthesized artifact downstream, not raw conflicting reports.
