---
name: pi-session-namer
description: >
  Rename pi coding agent sessions with a structured Chinese convention: [完成度][任务类型][(混杂)][工作概括].
  Use when the user says "重命名session", "命名当前会话", "给这个session起名", "rename session",
  or when a session has meaningful work but still bears a default/generic name.
  Also use after completing a significant task — proactively suggest renaming.
---

# Pi Session Namer

为 pi coding agent 的 session 按照统一格式命名。

## 命名格式

```
[完成/未完/待办][项目/调研/对话/助手][(可选)混杂][工作概括，含整体任务和最后一次任务细节]
```

四个字段：

| 字段 | 取值 | 判断依据 |
|---|---|---|
| **完成度** | `完成` / `未完` / `待办` | 任务是否已有最终产出。中断但有实质性进展→`未完`，仅讨论未动手→`待办` |
| **任务类型** | `项目` / `调研` / `对话` / `助手` | `项目`=编码/构建/配置产出物；`调研`=搜索/查文档/分析问题；`对话`=讨论/问答/无技术产出；`助手`=文件管理/格式转换等工具性操作 |
| **混杂** | 有则加`混杂`，无则省略 | 同一 session 跨越多个不相关主题时标记 |
| **概括** | 2-12 个中文字 | 先整体任务概述，分号后最后一次任务细节。如 `Pi Session批量重命名；对比npm扩展` |

**示例**：
- `[完成][项目][Pi Session批量重命名；规则沉淀为skill]`
- `[未完][调研][大模型API成本对比；Gemini vs Claude]`
- `[完成][对话][Python类型系统设计讨论]`
- `[待办][项目][混杂][多项目环境配置]`

## 执行流程

### 1. 分析对话历史

遍历当前 session 的消息，提取：
- 第一条用户消息 → 判断任务类型和初始意图
- 最后几条交互 → 判断完成度和最新进展
- 主题一致性 → 判断是否混杂

主动询问用户确认完成度（用户对自己工作完成度的判断最准确），其他字段可由 AI 推断。

### 2. 构造名称

按格式拼接四个字段，确保：
- 总长度控制在 80 字符以内
- 概括部分 2-12 个中文字，用分号分隔整体任务和最新细节
- 无多余空格、无引号包裹

### 3. 设置 session 名称

pi 提供了 `/name` 内置命令直接设置 session 名。优先使用：

```
/name [完成][项目][Pi Session批量重命名]
```

**备用方案**：如果 `/name` 不可用，直接编辑 session 文件。pi session 以 JSONL 格式存储，名称通过追加 `session_info` 行实现。详见 `references/pi-session-format.md`。

## 重要原则

- **不教条**：用户可能只想快速命名而不走完整格式。如果用户说"随便起个名"，就简化处理
- **完成度由用户确认**：AI 可以推断任务类型和概括，但完成度必须问用户
- **同名不覆盖**：如果 session 已有有意义的名称且用户未要求重命名，不主动修改
