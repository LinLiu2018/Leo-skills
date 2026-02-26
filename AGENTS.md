# AGENTS.md - Leo AI System Workspace

This is the Leo AI System workspace. All behavior, conventions, and workflows are defined here.

## Every Session Checklist

Before doing anything else:

1. Check `docs/planning/task_plan.md` — current task status (if exists)
2. Read `leo_knowledge/context/user_profile.md` — who you are helping
3. Read `leo_knowledge/context/development_guide.md` — coding standards
4. Read `leo_knowledge/context/capability_index.md` — avoid duplicating existing capabilities
5. If implementing code, read `leo_knowledge/context/system_architecture.md`

Do not skip these steps. Context loading prevents wasted effort.

## System Overview

Leo AI System is an AI-powered personal assistant platform with:

- **107 Skills** across 17 categories
- **9 Agents** for domain-specific tasks
- **5 Workflows** for multi-step orchestration
- **Orchestrator** (`leo_orchestrator`) for intent recognition and routing
- **Memory** (`leo_memory`) for cross-session persistence
- **External integrations**: OpenClaw (Feishu gateway), Superpowers (dev workflows)

## Core Workflow: Intent > Agent > Skill

```
User Input
    |
    v
Intent Recognizer (leo_orchestrator/intent_recognizer.py)
    |
    +--> Agent dispatch (9 agents, keyword-matched)
    |        |
    |        v
    |    Agent executes using Skills
    |
    +--> Skill direct execution (107 skills)
    |
    +--> Workflow orchestration (multi-agent pipelines)
```

**Key modules:**

| Module | Path | Purpose |
|--------|------|---------|
| Intent Recognizer | `src/leo_orchestrator/intent_recognizer.py` | Route user input |
| Workflow Engine | `src/leo_orchestrator/workflow_engine.py` | Multi-step pipelines |
| Shared Memory | `src/leo_memory/shared_memory.py` | Cross-session persistence |
| Capability Index | `leo_knowledge/context/capability_index.md` | Auto-generated registry |

## Context Engineering

For complex tasks (3+ steps, research, multi-tool), use planning files:

| File | Purpose | When to Update |
|------|---------|----------------|
| `docs/planning/task_plan.md` | Phases, progress, decisions | Before starting; after each phase |
| `docs/research/findings.md` | Research results, technical decisions | Every 2 searches/browses |
| `docs/progress/progress.md` | Session logs, test results | End of each work session |

**Rules:**

1. Complex tasks: create `task_plan.md` first
2. Every 2 searches: update `findings.md`
3. Before decisions: re-read the plan file
4. Document all errors; never repeat a failure

## Memory

You wake up fresh each session. Files are your continuity.

- **Memory is limited** — if you want to remember something, WRITE IT TO A FILE
- "Mental notes" do not survive session restarts. Files do.
- When someone says "remember this" — update the relevant file
- When you learn a lesson — document it so future-you does not repeat it
- **Text > Brain**

**Memory locations:**

| Type | Location |
|------|----------|
| Shared memory (structured) | `src/leo_memory/shared_memory.py` |
| Context files (static) | `leo_knowledge/context/` |
| Task planning (dynamic) | `docs/planning/` |
| Research findings | `docs/research/` |
| Progress logs | `docs/progress/` |

## Safety

- Do not exfiltrate private data. Ever.
- Do not run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

**Safe to do freely:**

- Read files, explore, organize, learn
- Search the web
- Work within this workspace

**Ask first:**

- Sending emails, public posts
- Anything that leaves the machine
- Anything you are uncertain about

## Skill Development Conventions

### Naming

- All directories and files: `snake_case` (no hyphens, no spaces, no uppercase)
- Skills: `{function}_skill` (e.g., `web_search_skill`)
- Agents: `{domain}_agent` (e.g., `research_agent`)
- Workflows: `{business}_pipeline` (e.g., `content_pipeline`)

### Required Structure

```
{skill_name}_skill/
├── SKILL.md              # Required: skill definition with YAML frontmatter
├── __init__.py            # Package init
├── {skill_name}_skill.py  # Main class (optional)
├── scripts/
│   └── main.py            # Entry point
└── config/                # Configuration (optional)
```

### SKILL.md Frontmatter

Every SKILL.md must include YAML frontmatter:

```yaml
---
name: skill_name
version: 1.0.0
category: tools
description: Brief description
triggers:
  - "trigger_word_1"
  - "trigger_word_2"
author: Leo Liu
---
```

Supported frontmatter fields: `name`, `description`, `compatibility`, `license`, `metadata`.
Custom fields go under `metadata`. Do not use `|` multiline format for `description`.

### Before Creating a New Skill

1. Search `leo_knowledge/context/capability_index.md` for existing capabilities
2. Check for naming conflicts
3. Assess capability overlap with existing skills
4. Follow the naming convention strictly

## File Path Rules

```
Root (entry points and config only):
├── CLAUDE.md              # System entry (required)
├── AGENTS.md              # This file
├── README.md              # Project description
├── .claude/               # Claude configuration
├── src/                   # Source code
├── projects/              # Project files
└── leo_knowledge/         # Knowledge base (static context)

docs/ (all documentation):
├── identity/              # Identity: IDENTITY.md, SOUL.md, USER.md
├── reference/             # Indices: AGENTS.md, TOOLS.md, SKILLS_MANIFEST.md
├── guides/                # How-to guides
├── planning/              # Task plans: task_plan.md, implementation_plan.md
├── progress/              # Session logs: progress.md
├── research/              # Findings: findings.md, reports/
└── memory/                # Shared memory (optional)
```

**Rule:** New files go into the appropriate `docs/` subdirectory. Do not place files in the root directory.

## Common Commands

```bash
# Update capability index
python scripts/maintenance/update_capability_index.py

# Validate project structure
python scripts/development/validate_structure.py

# Standardize SKILL.md files (preview)
python scripts/development/standardize_skills.py --dry-run

# Run quick tests
python scripts/testing/quick_test.py

# Run full test suite
pytest tests/
```

## External Integrations

### OpenClaw (Feishu Gateway)

- Config: `C:\Users\刘方林\.openclaw\openclaw.json`
- Start: `cd D:\openclaw && node openclaw.mjs gateway --port 18789`
- Dashboard: `openclaw dashboard`
- Troubleshooting: see `CLAUDE.md` section 5

### Superpowers (Dev Workflows, v4.2.0)

- 14 development workflow skills from [obra/superpowers](https://github.com/obra/superpowers)
- Original: `~/.claude/skills/superpowers/`
- Leo equivalents: `src/leo_skills/` (snake_case Chinese versions)
- Reference docs: `docs/reference/superpowers/`
- Hook: `.claude/hooks.json` (SessionStart auto-injection)

**Recommended dev flow:**

```
brainstorming -> writing_plans -> executing_plans -> finishing_work
```

