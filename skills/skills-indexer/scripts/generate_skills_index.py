#!/usr/bin/env python3
"""Generate skills-index.md and skills-index.json for the current project.

Scans local, global OpenCode, and global multi-agent skills to map capabilities.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_frontmatter(content: str):
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    yaml_block = content[3:end].strip()
    result = {}
    for line in yaml_block.splitlines():
        match = re.match(r"^(\w+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            result[key] = value.strip()
    return result


def scan_skills_dir(path: Path, scope: str):
    """Recursively find SKILL.md files and extract metadata."""
    skills = []
    if not path.exists():
        return skills
    for skill_file in path.rglob("SKILL.md"):
        rel = skill_file.relative_to(path).as_posix()
        try:
            content = skill_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = skill_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        name = fm.get("name", skill_file.parent.name)
        desc = fm.get("description", "(no description)")
        skills.append({
            "name": name,
            "description": desc,
            "location": rel,
            "full_path": str(skill_file),
            "scope": scope,
            "dir_name": skill_file.parent.name,
        })
    return skills


def main():
    work_dir = Path(os.environ.get("WORK_DIR", os.getcwd())).resolve()
    out_dir = work_dir / ".orchestrator"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    warnings = []

    # 1. Project-local skills
    project_paths = [
        (work_dir / ".opencode" / "skills", "project/opencode"),
        (work_dir / ".gemini" / "skills", "project/gemini"),
        (work_dir / "skills", "project"),
    ]
    for pp, scope_name in project_paths:
        if pp.exists():
            results.extend(scan_skills_dir(pp, scope_name))

    # 2. Global OpenCode skills
    global_opencode = Path(os.path.expanduser("~/.config/opencode/skills")).resolve()
    if global_opencode.exists() and global_opencode != work_dir:
        results.extend(scan_skills_dir(global_opencode, "global/opencode"))

    # 3. Global Multi-Agent skills
    global_agents = Path(os.path.expanduser("~/.agents/skills")).resolve()
    if global_agents.exists() and global_agents != work_dir:
        results.extend(scan_skills_dir(global_agents, "global/agents"))

    # Agent mapping rules for all skills (including new gemini-skills)
    agent_map = {
        "doc-update": ["doc-maintainer"],
        "doc-scaffold": ["doc-maintainer"],
        "doc-audit": ["doc-maintainer", "reviewer-critic"],
        "doc-pruner": ["doc-maintainer"],
        "doc-transfer": ["doc-maintainer"],
        "architecture-update": ["architect-planner"],
        "dependency-auditor": ["architect-planner", "researcher-explorer"],
        "deep-auditor": ["reviewer-critic", "security-auditor"],
        "multi-agent-scanner": ["reviewer-critic", "security-auditor"],
        "code-verifier": ["integrator-qa", "code-reviewer"],
        "code-review": ["code-reviewer"],
        "commit-reviewer": ["reviewer-critic", "code-reviewer"],
        "plan-creator": ["architect-planner", "researcher-explorer"],
        "plan-reviewer": ["reviewer-critic", "architect-planner"],
        "plan-refiner": ["architect-planner"],
        "peer-reviewer": ["reviewer-critic"],
        "feature-implementer": ["implementer-builder"],
        "test-generator": ["test-engineer"],
        "debug-analyzer": ["debug"],
        "context-search": ["researcher-explorer", "architect-planner"],
        "context-builder": ["researcher-explorer"],
        "session-handoff": [],
        "project-discovery": ["researcher-explorer"],
        "agentic-orchestrator": ["orchestrator-conductor"],
        "find-skills": ["orchestrator-conductor"],
        "frontend-design": ["ux-designer", "implementer-builder"],
        "ui-ux-pro-max": ["ux-designer"],
        "webapp-testing": ["integrator-qa", "test-engineer"],
        "writer": ["content-writer"],
        "xlsx": ["data-analyst"],
        "docx": ["content-writer"],
        "pptx": ["content-writer"],
        "pdf": ["content-writer"],
        "vercel-deploy": ["integrator-qa"],
        "vercel-react-best-practices": ["architect-planner", "reviewer-critic"],
        "web-design-guidelines": ["ux-designer", "reviewer-critic"],
        "brand-guidelines": ["ux-designer", "content-writer"],
        "canvas-design": ["ux-designer"],
        "discovery-interview": ["architect-planner"],
        "doc-coauthoring": ["content-writer", "doc-maintainer"],
        "mcp-builder": ["implementer-builder"],
        "ponytail": ["implementer-builder"],
        "ponytail-review": ["reviewer-critic"],
        "ponytail-help": ["orchestrator-conductor"],
        "ralph": ["architect-planner"],
        "prd": ["architect-planner"],
        "remotion": ["content-writer"],
        "remotion-best-practices": ["content-writer"],
        "stitch-loop": ["implementer-builder"],
        "theme-factory": ["ux-designer"],
        "web-artifacts-builder": ["implementer-builder"],
        "agentation": ["ux-designer", "implementer-builder"],
        "agentation-self-driving": ["ux-designer"],
        "caveman": ["orchestrator-conductor"],
        "obsidian": ["researcher-explorer"],
    }

    # Deduplicate keeping local over global
    dedup = {}
    # Sort results so global are processed first, project-local overwrites them
    results_sorted = sorted(
        results,
        key=lambda x: (0 if "global" in x["scope"] else 1)
    )
    for s in results_sorted:
        name = s["name"]
        dedup[name] = s
    final = sorted(dedup.values(), key=lambda x: x["name"])

    # Build JSON
    json_skills = []
    for s in final:
        suggested = agent_map.get(s["name"], [])
        json_skills.append({
            "name": s["name"],
            "description": s["description"],
            "location": s["location"],
            "scope": s["scope"],
            "suggested_agents": suggested,
            "tags": [],
        })

    stats = {
        "total": len(final),
        "mapped": sum(1 for s in json_skills if s["suggested_agents"]),
        "unmapped": sum(1 for s in json_skills if not s["suggested_agents"]),
    }

    index_json = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "work_dir": str(work_dir),
        "scopes_scanned": [
            {"path": ".opencode/skills/", "scope": "project/opencode"},
            {"path": ".gemini/skills/", "scope": "project/gemini"},
            {"path": "~/.config/opencode/skills/", "scope": "global/opencode"},
            {"path": "~/.agents/skills/", "scope": "global/agents"},
        ],
        "stats": stats,
        "skills": json_skills,
        "warnings": warnings,
    }

    # Build Markdown
    lines = []
    lines.append("# Skills Index")
    lines.append("")
    lines.append("Auto-generated skills registry.")
    lines.append(f"- **Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
    lines.append(f"- **Work Directory**: `{work_dir}`")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total skills | {stats['total']} |")
    lines.append(f"| Mapped to agents | {stats['mapped']} |")
    lines.append(f"| Unmapped | {stats['unmapped']} |")
    lines.append("")
    lines.append("## Skills")
    lines.append("")
    lines.append("| Skill | Scope | Description | Suggested Agents |")
    lines.append("|-------|-------|-------------|------------------|")
    for s in final:
        suggested = ", ".join(agent_map.get(s["name"], [])) or "—"
        lines.append(f"| `{s['name']}` | {s['scope']} | {s['description']} | {suggested} |")
    lines.append("")

    lines.append("## Unmapped Skills")
    lines.append("")
    unmapped = [s for s in final if s["name"] not in agent_map]
    if not unmapped:
        lines.append("_None — all skills are mapped._")
    else:
        for s in sorted(unmapped, key=lambda x: x["name"]):
            lines.append(f"- `{s['name']}` ({s['scope']}) — {s['description']}")
    lines.append("")

    # Write outputs
    json_path = out_dir / "skills-index.json"
    md_path = out_dir / "skills-index.md"

    json_path.write_text(json.dumps(index_json, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {json_path} ({json_path.stat().st_size} bytes)")
    print(f"Wrote {md_path} ({md_path.stat().st_size} bytes)")
    print(f"Total skills: {stats['total']} | Mapped: {stats['mapped']} | Unmapped: {stats['unmapped']}")


if __name__ == "__main__":
    main()
