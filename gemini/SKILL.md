---
description: Gemini CLI for one-shot Q&A, summaries, and generation.
homepage: https://ai.google.dev/
metadata:
    local-path: C:\Users\Ryle_\.agents\skills\gemini
    openclaw:
        emoji: ✨
        install:
            - bins:
                - gemini
              formula: gemini-cli
              id: brew
              kind: brew
              label: Install Gemini CLI (brew)
        requires:
            bins:
                - gemini
name: gemini
---
# Gemini CLI

Use Gemini in one-shot mode with a positional prompt (avoid interactive mode).

Quick start

- `gemini "Answer this question..."`
- `gemini --model <name> "Prompt..."`
- `gemini --output-format json "Return JSON"`

Extensions

- List: `gemini --list-extensions`
- Manage: `gemini extensions <command>`

Notes

- If auth is required, run `gemini` once interactively and follow the login flow.
- Avoid `--yolo` for safety.
