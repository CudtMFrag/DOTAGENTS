---
name: skill-evaluator
description: >
  Use when the user wants to find, compare, and choose the best agent skills for a specific task. Also use when the user asks "what skill should I use for X", "compare these skills", or wants to validate that installed skills work together without conflicts.
---

# Skill Evaluator

Find the right skill and verify it's actually good before recommending it.

## First: Is a skill even the answer?

Skills aren't always the right tool. Before searching, briefly consider:

- **Prompt** — one-off task, no reuse needed
- **Instruction** (CLAUDE.md / rules) — always-on rules, file-scoped conventions
- **Hook** — deterministic enforcement (pre-commit, on-save)
- **Skill** — reusable packaged workflow with references, scripts, or deep domain knowledge

If the answer isn't skill, say so and recommend the right primitive. Don't force a skill search.

## Core principle: Install and read

**This is what separates evaluation from a simple search.** Most skill-finder tools stop at the registry description. Registry descriptions can be stale, misleading, or outright wrong. The only way to know what a skill actually does is to install it and read the source.

## Discovery

Search broadly — different query angles surface different candidates. Use `npx skills find` with varied phrasings, check skills.sh if helpful, and cross-check GitHub Marketplace for GitHub Actions skills specifically.

## Evaluation

Install each serious candidate, then read the actual files. Pay attention to:

- Does SKILL.md actually deliver what the description promised?
- Are reference files substantive or generic filler?
- Are scripts functional or placeholder stubs?
- Is there cross-contamination (files from unrelated frameworks)?
- Is the repo maintained or abandoned?

**Let the source code be the evidence.** Don't score from the registry description alone.

Compare candidates holistically across the dimensions that matter for the user's specific task. Weigh task relevance most heavily, then functional depth and actionability. Present the comparison with specific evidence from source code — not just scores, but concrete observations.

## Compatibility

When recommending multiple skills, check how they interact:

- Do their trigger conditions overlap in ways that could conflict?
- Do they have incompatible behavioral requirements?
- Can they be assigned clear, non-overlapping roles in a shared workflow?

## Cleanup

After the decision, remove installed skills that weren't selected. Verify the final stack with `npx skills list`.
