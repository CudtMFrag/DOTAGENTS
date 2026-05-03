# DOTAGENTS · 个人 AI Agent 技能集

[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 🇨🇳 中文

### 这是什么？

`DOTAGENTS` 是一个面向 AI Coding Agent（如 Claude Code、Cursor、Codex、Pi 等）的技能集合仓库。仓库中的每个技能都是一个独立的 `SKILL.md` 文件，包含专业化的指令、脚本和参考文档，Agent 会在运行时动态加载它们以处理特定任务。

### 安装方式

使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 安装：

```bash
npx skills add CudtMFrag/DOTAGENTS -a <你的agent名> -y
```

### 技能清单

#### 🔧 UniversalSkill（通用技能）

| 技能 | 说明 |
|---|---|
| **skill-evaluator** | 为特定任务寻找、比较并选择最佳 Agent 技能。处理完整评估管线：推荐门控、多源发现、表面过滤、深度验证、多维评分和跨技能兼容性分析。 |
| **env-adapter** | 检测当前开发环境并适配所有操作。在任何编程任务前使用——会话开始时、打开项目时、切换机器时、命令因平台问题失败时，或用户询问环境兼容性时。 |
| **project-scaffold** | 使用标准目录结构、配置文件和包管理器感知初始化新项目。支持多种项目类型（Node.js、Python、Go 等）。 |

#### 🎯 SpecializedSkill（专项技能）

| 技能 | 说明 |
|---|---|
| **tag-reductor** | 归约式内容标签——从文章/书签/聊天集合中提取扁平、简短的标签，生成词云和共现关系图可视化。适用于"分析标签"、"归类标签"、"打标签"、"标签归约"等指令。 |

### 目录结构

```
DOTAGENTS/
├── UniversalSkill/          # 通用技能
│   ├── skill-evaluator/
│   │   └── SKILL.md
│   ├── env-adapter/
│   │   └── SKILL.md
│   └── project-scaffold/
│       └── SKILL.md
├── SpecializedSkill/        # 专项技能
│   └── tag-reductor/
│       ├── SKILL.md
│       └── scripts/         # 辅助脚本
└── README.md
```

### 贡献

本仓库为个人使用，但欢迎提 Issue 或 PR 讨论改进。

---

<a name="english"></a>
## 🇬🇧 English

### What is this?

`DOTAGENTS` is a curated collection of skills for AI Coding Agents (Claude Code, Cursor, Codex, Pi, etc.). Each skill is a standalone `SKILL.md` file containing specialized instructions, scripts, and reference docs that agents load dynamically at runtime to handle specific tasks.

### Installation

Install via the [Vercel Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add CudtMFrag/DOTAGENTS -a <your-agent-name> -y
```

### Skill Inventory

#### 🔧 UniversalSkill

| Skill | Description |
|---|---|
| **skill-evaluator** | Find, compare, and choose the best agent skills for a specific task. Handles the full evaluation pipeline: recommendation gate, multi-source discovery, surface filtering, deep verification (install & read source), multi-dimensional scoring, and cross-skill compatibility analysis. |
| **env-adapter** | Detect the current development environment and adapt all operations accordingly. Use before any coding task — at the start of every conversation, when opening a project, when switching machines, when commands fail due to platform issues, or whenever the user asks about environment compatibility. |
| **project-scaffold** | Initialize new projects with standard directory structure, config files, and package manager awareness. Supports multiple project types (Node.js, Python, Go, etc.). |

#### 🎯 SpecializedSkill

| Skill | Description |
|---|---|
| **tag-reductor** | Reductionist content tagging — extract flat, short tags from article/bookmark/chat collections, generate word cloud and co-occurrence graph visualizations. Ideal for taxonomy distillation from any saved content collection. |

### Directory Structure

```
DOTAGENTS/
├── UniversalSkill/          # General-purpose skills
│   ├── skill-evaluator/
│   │   └── SKILL.md
│   ├── env-adapter/
│   │   └── SKILL.md
│   └── project-scaffold/
│       └── SKILL.md
├── SpecializedSkill/        # Domain-specific skills
│   └── tag-reductor/
│       ├── SKILL.md
│       └── scripts/         # Utility scripts
└── README.md
```

### Contributing

This is a personal collection, but Issues and PRs for improvements are welcome.

---

**License:** MIT
