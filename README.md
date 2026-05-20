# DOTAGENTS · Personal AI Agent Toolkit

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## 🇬🇧 English

### What is this?

`DOTAGENTS` is my collection of skills.

Extensions are published as separate npm packages (e.g. `pi install npm:pi-no-autowrite`).

### Installation

Install via the [Vercel Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add CudtMFrag/DOTAGENTS -a <your-agent-name> -y
```

### Skill Inventory

#### 🔧 UniversalSkill

| Skill | Description |
|---|---|
| **skill-evaluator** | Find, compare, and choose the best agent skills for a specific task. Handles the full evaluation pipeline: recommendation gate, multi-source discovery, surface filtering, deep verification (install & read source), multi-dimensional scoring, and cross-skill compatibility analysis. Above is AI shit, don't trust. |
| **env-adapter** | Detect the current development environment and adapt all operations accordingly. Use before any coding task — at the start of every conversation, when opening a project, when switching machines, when commands fail due to platform issues, or whenever the user asks about environment compatibility. |
| **project-scaffold** | Initialize new projects with standard directory structure, config files, and package manager awareness. Supports multiple project types (Node.js, Python, static HTML, etc.). |
| **activity-watch** | ActivityWatch time tracking assistant. Help users categorize activities, analyze time usage, write queries for the Web UI query editor, and find focus patterns. Covers the query language, categorization rules, and common analysis recipes. |
| **skill-publish** | Publish skills to the DOTAGENTS repo and install globally. Covers the full workflow: create skills in UniversalSkill/SpecializedSkill, update README, git commit + push, install via `npx skills add` to all agents. |

#### 🎯 SpecializedSkill

| Skill | Description |
|---|---|
| **tag-reductor** | Reductionist content tagging — extract flat, short tags from article/bookmark/chat collections, generate word cloud and co-occurrence graph visualizations. Ideal for taxonomy distillation from any saved content collection. |
| **daily-game-podcast** | Fetch all unread from Folo Kite News Gaming feed, compose a Chinese gaming news podcast script, convert to MP3 via xAI TTS, auto-mark as read. |

### Directory Structure

```
DOTAGENTS/
├── UniversalSkill/           # General-purpose skills
│   ├── activity-watch/
│   │   └── SKILL.md
│   ├── env-adapter/
│   │   └── SKILL.md
│   ├── project-scaffold/
│   │   └── SKILL.md
│   ├── skill-evaluator/
│   │   └── SKILL.md
│   └── skill-publish/
│       └── SKILL.md
├── SpecializedSkill/         # Domain-specific skills
│   ├── tag-reductor/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── daily-game-podcast/
│       ├── SKILL.md
│       └── scripts/
├── package.json
└── README.md
```

### Contributing

This is a personal collection, but Issues and PRs for improvements are welcome.

---

<a name="中文"></a>
## 🇨🇳 中文

### 这是什么？

`DOTAGENTS` 是我的技能集合仓库。

扩展已拆分为独立 npm 包（如 `pi install npm:pi-no-autowrite`）。

### 安装方式

使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 安装：

```bash
npx skills add CudtMFrag/DOTAGENTS -a <你的agent名> -y
```

### 技能清单

#### 🔧 UniversalSkill（通用技能）

| 技能 | 说明 |
|---|---|
| **skill-evaluator** | 为特定任务寻找、比较并选择最佳 Agent 技能。处理完整评估管线：推荐门控、多源发现、表面过滤、深度验证（安装并阅读源码）、多维评分和跨技能兼容性分析。以上为AI生成，建议谨慎相信。 |
| **env-adapter** | 检测当前开发环境并适配所有操作。在任何编程任务前使用——会话开始时、打开项目时、切换机器时、命令因平台问题失败时，或用户询问环境兼容性时。 |
| **project-scaffold** | 使用标准目录结构、配置文件和包管理器感知初始化新项目。支持多种项目类型（Node.js、Python、静态 HTML 等）。 |
| **activity-watch** | ActivityWatch 时间追踪助手。帮助用户分类活动、分析时间使用、为 Web UI 查询编辑器编写查询，以及发现专注模式。覆盖查询语言、分类规则和常见分析场景。 |
| **skill-publish** | 将技能发布到 DOTAGENTS 仓库并全局安装。覆盖完整工作流：在 UniversalSkill/SpecializedSkill 中创建技能、更新 README、Git commit + push、通过 `npx skills add` 安装到所有 agent。 |

#### 🎯 SpecializedSkill（专项技能）

| 技能 | 说明 |
|---|---|
| **tag-reductor** | 归约式内容标签——从文章/书签/聊天集合中提取扁平、简短的标签，生成词云与共现图。适用于标签分类体系蒸馏场景。 |
| **daily-game-podcast** | 从 Folo Kite News 游戏频道拉取全部未读条目，生成中文游戏新闻播客稿，通过 xAI TTS 转为 MP3 语音，自动标记已读。 |

### 目录结构

```
DOTAGENTS/
├── UniversalSkill/           # 通用技能
│   ├── activity-watch/
│   │   └── SKILL.md
│   ├── env-adapter/
│   │   └── SKILL.md
│   ├── project-scaffold/
│   │   └── SKILL.md
│   ├── skill-evaluator/
│   │   └── SKILL.md
│   └── skill-publish/
│       └── SKILL.md
├── SpecializedSkill/         # 专项技能
│   ├── tag-reductor/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── daily-game-podcast/
│       ├── SKILL.md
│       └── scripts/
├── package.json
└── README.md
```

### 贡献

本仓库为个人使用，但欢迎提 Issue 或 PR 讨论改进。

---

**License:** MIT
