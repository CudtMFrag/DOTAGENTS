---
name: skill-publish
description: >
  Publish a skill to the user's DOTAGENTS repository and install it globally across all agents. Covers the full workflow: create/edit SKILL.md in G:\00-DOTAGENTS\UniversalSkill\ (general-purpose) or SpecializedSkill\ (domain-specific), update README.md, git commit with Conventional Commits, push to GitHub (CudtMFrag/DOTAGENTS), and install via `npx skills add`. Use when the user finishes creating or editing a skill and wants to publish it, or asks "发布技能", "publish skill", "上传技能", "安装回来", "同步到所有 agent".
---

# Skill Publish

Publish a skill from the local DOTAGENTS repo to GitHub and install it globally across all agents via the Vercel Skills CLI.

## The DOTAGENTS repo

```
G:\00-DOTAGENTS\
├── UniversalSkill/      ← general-purpose skills (anyone can use)
│   ├── env-adapter/
│   ├── project-scaffold/
│   ├── skill-evaluator/
│   └── activity-watch/
├── SpecializedSkill/    ← domain-specific skills
│   └── tag-reductor/
└── README.md
```

**Rule**: generic, reusable skills → `UniversalSkill/`. Domain-specific, niche skills → `SpecializedSkill/`.

## Step 1: Create or edit the skill

Each skill is a directory with at least a `SKILL.md`:

```
skill-name/
└── SKILL.md   ← YAML frontmatter (name, description) + Markdown body
```

A valid SKILL.md frontmatter:

```yaml
---
name: skill-name
description: >
  What the skill does and when it triggers. Be specific and "pushy" —
  include trigger phrases and contexts so Claude knows when to invoke it.
---
```

The skill body should explain the WHY, not just the WHAT. Don't write step-by-step SOPs — describe goals, constraints, and key knowledge the model needs.

Optional bundled resources:
```
skill-name/
├── SKILL.md
├── scripts/      ← executable code for repetitive tasks
├── references/   ← docs loaded on demand
└── assets/       ← templates, icons, fonts
```

## Step 2: Update README.md

If it's a new skill, add it to the skill table in `G:\00-DOTAGENTS\README.md`. Both the Chinese and English sections.

UniversalSkill example:
```markdown
| **my-skill** | 简短中文说明。 |

| **my-skill** | Short English description. |
```

## Step 3: Commit and push

```bash
cd G:/00-DOTAGENTS
git add UniversalSkill/<skill-name>/ README.md
git commit -m "feat: add <skill-name> skill — <brief purpose>"
git push
```

Commit messages follow Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`.

## Step 4: Install to your agents

**Never use `-a '*'` — it creates junk directories for every agent `npx skills` has ever heard of, not just the ones you actually use.**

First, find your real agents:

```bash
npx skills list -g --json
```

Look at the output — each skill has an `agents` array. The agents with many skills listed are the ones you actually use. Pick their names (in kebab-case), then install with one `-a` flag per agent:

```bash
npx skills add CudtMFrag/DOTAGENTS -s <skill-name> -a <agent1> -a <agent2> -g -y
```

This clones from GitHub, places the canonical copy in `~\.agents\skills\<skill-name>\`, universal-copies to the most compatible agent, and symlinks to the rest.

Flags:
- `-s <name>` — install only this skill (use `'*'` for all skills in the repo)
- `-a <agent>` — one flag per agent, repeat for multiple, use kebab-case names
- `-g` — global scope (not project-scoped)
- `-y` — skip prompts

**To update an existing skill** after pushing changes to GitHub:
```bash
npx skills update <skill-name>
```

## Reference: npx skills commands

```
skills add <repo>         Install from GitHub repo
skills remove [name]      Remove installed skills
skills list -g            List global skills
skills list -g --json     Machine-readable output
skills update [name]      Update to latest version
skills find [query]       Search for skills interactively
```

## Reference: repo structure conventions

| Convention | Rule |
|---|---|
| Universal vs Specialized | Generic and reusable → UniversalSkill. Niche/domain-specific → SpecializedSkill |
| Directory name | kebab-case, matches skill `name` in frontmatter |
| One SKILL.md per skill | The only required file |
| Bundled scripts | `scripts/` subdirectory, referenced from SKILL.md |
| README | Bilingual (CN + EN), two skill tables |
| Git | Conventional Commits, push only when user says "上传"/"push"/"发布" |
