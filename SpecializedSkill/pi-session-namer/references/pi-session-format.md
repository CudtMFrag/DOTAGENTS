# Pi Session 存储格式

## JSONL 文件结构

pi session 文件为 JSONL（每行一个 JSON 对象），存储在：

```
~/.pi/agent/sessions/{encoded-cwd}/{session-id}.jsonl
```

- Windows: `C:\Users\<user>\.pi\agent\sessions\--C--Users-<user>--\<timestamp>.jsonl`
- WSL: `//wsl.localhost/<distro>/home/<user>/.pi/agent/sessions/<encoded-cwd>/`

**cwd 编码规则**：路径中的 `\` 和 `/` 替换为 `--`。例如：
- `C:\Users\Ryle_` → `--C--Users-Ryle_--`
- `/home/user/projects` → `--home-user-projects`

## Session 名称的存储

名称通过 `session_info` 类型的条目追加到 JSONL 末尾：

```json
{"type": "session_info", "id": "a1b2c3d4", "parentId": "x9y8z7w6", "timestamp": "2026-06-06T12:00:00.000Z", "name": "我的会话名"}
```

pi 的 `getSessionName()` 从文件末尾向前扫描，取最新一条 `session_info.name`。

## 找到当前 session 文件

方法 1：通过环境变量。pi 可能设置 `PI_SESSION_ID` 或类似环境变量。

方法 2：查找最近修改的 JSONL：
```bash
# Windows PowerShell
Get-ChildItem "$env:USERPROFILE\.pi\agent\sessions\--C--Users-Ryle_--\*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# WSL/Linux
ls -t ~/.pi/agent/sessions/<encoded-cwd>/*.jsonl | head -1
```

方法 3：通过 session ID 匹配。如果知道 session ID，可以直接构造路径。

## 追加名称

```bash
# 读取最后一行获取 last entry id 作为 parentId
LAST_LINE=$(tail -1 "$SESSION_FILE")
LAST_ID=$(echo "$LAST_LINE" | jq -r '.id')
NEW_ID=$(openssl rand -hex 4)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

# 追加 session_info 行
echo "{\"type\":\"session_info\",\"id\":\"$NEW_ID\",\"parentId\":\"$LAST_ID\",\"timestamp\":\"$TIMESTAMP\",\"name\":\"[完成][项目][示例名称]\"}" >> "$SESSION_FILE"
```

**注意**：使用 `>>` 追加而非覆盖，确保不破坏已有数据。

## pi 内置命令

pi 提供 `/name` 命令直接设置 session 名：

```
/name [完成][项目][Pi Session批量重命名]
```

这是最可靠的方式，无需手动操作文件。优先使用。
