---
name: env-adapter
description: "Detect the current development environment and adapt all operations accordingly. Use BEFORE any coding task \u2014 at the start of every conversation, when opening a project, when switching machines, when commands fail due to platform issues, or whenever the user asks about environment compatibility. Triggers on: \"\u68c0\u6d4b\u73af\u5883\", \"check my environment\", \"why is this command failing\", \"switch to WSL\", \"run in Docker\", path format issues, shell selection questions."
---

# Environment Adapter

Detect the current environment dynamically — never assume OS, shell, or toolchain. Run this at the start of every substantive coding session.

## Detection sequence

Run the following checks and report findings to the user in a concise summary table:

### 1. OS & Runtime

```bash
uname -s
```
- `MSYS_*` / `MINGW*` / `CYGWIN*` → Git Bash on Windows
- `Linux` → check WSL or native Linux
- `Darwin` → macOS

### 2. Is this WSL?

```bash
cat /proc/version 2>/dev/null | grep -i "microsoft\|WSL"
```
If output contains "microsoft" or "WSL", we're inside WSL2.

### 3. Is this a Docker container?

```bash
test -f /.dockerenv && echo "YES" || echo "NO"
```
If in a container, note that paths are Linux-native and the filesystem may be isolated.

### 4. Available shells

```bash
which pwsh 2>/dev/null && echo "pwsh available" || echo "no pwsh"
which bash 2>/dev/null && echo "bash available" || echo "no bash"
```
**Rule**: pwsh available on Windows native → use `.ps1` scripts. Otherwise → use `.sh` scripts.

### 5. Available package managers

```bash
which uv 2>/dev/null && uv --version || echo "no uv"
which npm 2>/dev/null && npm --version || echo "no npm"
which pnpm 2>/dev/null && pnpm --version || echo "no pnpm"
which bun 2>/dev/null && bun --version || echo "no bun"
```

### 6. Git configuration

```bash
git config user.name 2>/dev/null || echo "NOT CONFIGURED"
git config user.email 2>/dev/null || echo "NOT CONFIGURED"
git branch --show-current 2>/dev/null || echo "NOT A GIT REPO"
git status --short 2>/dev/null | head -5
```

### 7. Project type

Check for these files (in order): `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `CMakeLists.txt`, `Makefile`.

### 8. DevContainer

```bash
ls .devcontainer/devcontainer.json 2>/dev/null && echo "DEVCONTAINER FOUND" || echo "no devcontainer"
```

## Output format

After detection, present findings as a compact table:

```
## 当前环境

| 项目 | 检测结果 |
|------|----------|
| 操作系统 | Windows (Git Bash) |
| WSL | 否 |
| Docker | 否 |
| Shell | bash ✓  pwsh ✓  → 使用 .sh 脚本 |
| 包管理器 | npm 10.x ✓  uv 0.x ✓ |
| Git | user.name=xxx  branch=master  (clean) |
| 项目类型 | Node.js (package.json) |
| DevContainer | 未配置 |
```

## Adaptation rules

Based on detection results, apply these rules:

1. **Shell selection**: pwsh available on native Windows → `.ps1`. WSL/container/Linux/macOS → `.sh`. Always put scripts in `scripts/`.
2. **Path format**: Always use forward slashes (`/`) in code and config files. When passing paths TO Windows-native commands (PowerShell, cmd.exe), convert to backslashes.
3. **Package manager**: Use `uv` for Python (never pip/poetry/conda). Use whatever JS package manager the project uses (check lock file: `package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `bun.lockb` → bun).
4. **Commands**: Never run raw `npm`/`pnpm`/`uv`/`python` from the conversation — always wrap in scripts under `scripts/`. Exception: environment detection itself.
5. **If in container**: Remind about volume mounts — files written inside the container may not persist unless the path is mounted.
6. **If DevContainer found**: Tell the user "这个项目已配置 DevContainer，VS Code 打开时会自动提示进入容器" and ask if they want to use it.

## When to re-detect

Re-run detection when:
- User switches between Windows and WSL
- User enters/exits a Docker container
- Commands fail with "command not found" or path errors
- User explicitly asks
