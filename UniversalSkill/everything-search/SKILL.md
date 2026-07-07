---
name: everything-search
description: Use Windows Everything/es.exe for ultra-fast local file search. Use this whenever a Windows user wants to find files or folders by name, path, extension, wildcard, or all-drive search, even if they do not mention Everything. Also use when fixing Everything IPC errors, starting Everything silently, waiting for indexing/query readiness, or writing PowerShell commands for Everything CLI. Do not use as a general web search or file-content search skill.
---

# Everything Search

Use this skill to help agents search Windows files through Everything CLI (`es.exe`) without depending on a pi extension.

Everything is Windows-only. On Linux/macOS, say that Everything/es.exe is not available natively and do not pretend to run it.

## Use cases

Use this when the user wants to:

- Find a file or folder somewhere on a Windows machine.
- Search by filename, wildcard, extension, or path fragment.
- Search all drives quickly.
- Recover from `Everything IPC not found`.
- Start Everything silently before searching.
- Write shell/PowerShell commands that use Everything CLI.

## Required tools

- `Everything.exe` installed.
- `es.exe` available in PATH.

Recommended install on Windows:

```powershell
scoop install everything-beta everything-cli
```

## Quick commands

Check CLI:

```powershell
where es.exe
es.exe -get-everything-version
```

Search all drives:

```powershell
es.exe -n 20 "毕业论文最终版"
```

Search by extension:

```powershell
es.exe -n 50 ext:pdf
```

Search under a path:

```powershell
es.exe -path "C:\Users" -n 50 "*.docx"
```

JSON output for agents:

```powershell
es.exe -json -name -path-column -size -date-modified -date-format 1 -n 20 "package.json"
```

Regex:

```powershell
es.exe -json -name -path-column -regex -n 20 ".*\.config\..*"
```

Files only:

```powershell
es.exe -json -name -path-column /a-d -n 20 ext:exe
```

Legacy 1.5 alpha instance:

```powershell
es.exe -instance 1.5a -get-everything-version
es.exe -instance 1.5a -json -name -path-column -n 20 ext:ts
```

## IPC recovery

If `es.exe` reports `Everything IPC not found`, do this:

1. Locate `Everything.exe`.
2. Start it silently with `-startup`.
3. Poll `es.exe -get-everything-version`.
4. Run `es.exe -json -n 1 *` to confirm query readiness.
5. Retry the user's search.

Use bundled script when available:

```powershell
pwsh -NoProfile -File scripts/check-everything.ps1 -Start
pwsh -NoProfile -File scripts/search-everything.ps1 -Query "ext:ts" -MaxResults 20 -AutoStart
```

## Output style

When giving commands, prefer PowerShell on Windows. Keep output actionable:

- Command to run.
- What success looks like.
- What to do if IPC still fails.

For user-facing search results, summarize top matches with full paths. If returning JSON, keep it machine-readable.

## Troubleshooting

### `es.exe` missing

Tell user to install Everything CLI or add `es.exe` to PATH.

```powershell
scoop install everything-cli
```

### `Everything.exe` missing

Tell user to install Everything or pass a full path to the script.

```powershell
scoop install everything-beta
```

### Privilege mismatch

If terminal/agent runs as administrator while Everything runs as normal user, IPC can fail. Run both at the same privilege level.

### Non-Windows

Everything/es.exe is Windows-only. Do not try to install or launch it on Linux/macOS. Explain that this workflow must run on Windows, or ask for access to the Windows machine.
