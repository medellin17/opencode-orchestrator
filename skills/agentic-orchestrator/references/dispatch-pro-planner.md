# Dispatch Template: Pro Planner

Use this template when dispatching `architect-planner-pro`. The pro planner runs on
a stronger model, but it still needs a **curated Context Brief** from you. Do not
dump raw `researcher-explorer` output and hope the pro planner will sort it out.

## Required Context Brief Structure

```
## Context Brief

### User Goal
[Original request, verbatim]

### Scope
- In scope: ...
- Out of scope: ...

### Constraints
[Tech stack, patterns, non-negotiables]

### Key Files
| File | Relevance |
|------|-----------|
| `path/to/file.py` | Brief note |

### Existing Patterns
[How this project solves similar problems]

### Risks Flagged
[Security, performance, compatibility concerns]

### Research Findings
[Raw or summarized output from researcher-explorer]
```

Then attach the actual file contents or snippets the planner must see.

## Example Dispatch

```
task({
  description: "Design OAuth2 architecture",
  prompt: `You are architect-planner-pro. Design a complete OAuth2 architecture for
our FastAPI backend.

## Goal
Produce a detailed implementation plan for adding Google + GitHub OAuth2 flows,
including token handling, user linking, and security considerations.

## Context Brief

### User Goal
Add OAuth2 (Google + GitHub) to the FastAPI backend so users can sign in with
third-party providers.

### Scope
- In scope: OAuth2 authorization-code flow, provider userinfo mapping, JWT session
  tokens, account linking by email.
- Out of scope: passwordless email login, SAML, mobile SDKs.

### Constraints
- FastAPI + SQLAlchemy + PostgreSQL.
- Existing auth uses JWT with bcrypt in src/auth.py.
- Must reuse existing User model; no schema rewrites.

### Key Files
| File | Relevance |
|------|-----------|
| src/auth.py | Existing JWT login, bcrypt hashing |
| src/models/user.py | User schema |
| src/config.py | Settings loader |

### Existing Patterns
- JWT tokens are issued in src/auth.py::create_access_token.
- User lookup is by email.

### Risks Flagged
- Account takeover if provider email is not verified.
- Token leakage if OAuth state is weak.

### Research Findings
[copy-paste the relevant parts of researcher-explorer output here]

## Deliverable
A markdown plan saved to data/tasks/oauth/plan.md with these sections:
Goal, Context, Architecture, Implementation Plan (stages), Interface Definitions,
Risks & Mitigations, Out of Scope, Design Uncertainty, Confidence.

## Constraints
- Do NOT write implementation code.
- Be specific about file paths and signatures.
- Flag any assumption you make about existing code.
- Include honest Confidence and Design Uncertainty sections.`,
  subagent_type: "architect-planner-pro"
})
```
