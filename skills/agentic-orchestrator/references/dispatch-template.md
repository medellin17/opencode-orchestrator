# Dispatch Templates

This folder contains `task()` dispatch templates for different orchestration cases.
Pick the one that matches your current dispatch:

| Template | Use when |
|----------|----------|
| [`dispatch-simple.md`](dispatch-simple.md) | Default case: any single sub-agent call on a weak model. Includes prompt structure, weak-model mindset, and basic examples. |
| [`dispatch-pro-planner.md`](dispatch-pro-planner.md) | Dispatching `architect-planner-pro`. Requires a curated Context Brief. |
| [`dispatch-parallel.md`](dispatch-parallel.md) | Launching multiple independent sub-agents simultaneously (cheap models only). |

**Rule of thumb:**
- One cheap agent → `dispatch-simple.md`.
- Pro planner → `dispatch-pro-planner.md`.
- Multiple cheap agents in parallel → `dispatch-parallel.md`.
