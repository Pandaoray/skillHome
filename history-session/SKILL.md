---
name: history-session
description: "Display historical Claude Code sessions for the current directory, letting users decide whether to --resume a previous session. Reads sessions-index.json and .jsonl files from ~/.claude/projects/. Use when user types /history-session or says '历史会话', 'history session', '查看历史', '看看历史会话'."
---

# history-session Skill

展示当前目录（`$PWD`）下的 Claude Code 历史会话列表，让用户决定是否通过 `--resume` 恢复。

## 触发条件

用户输入以下任意内容时调用此 skill：
- `/history-session`
- "历史会话"、"history session"、"查看历史"、"看看历史会话"

## 执行步骤

**Step 1：运行以下脚本获取历史会话数据**

```bash
python3 - "$PWD" <<'PYEOF'
import json, os, sys
from datetime import datetime, date

pwd = sys.argv[1]
claude_dir = os.path.expanduser("~/.claude")
projects_dir = os.path.join(claude_dir, "projects")

sessions = {}  # key: full session_id, value: dict

def relative_date(date_str):
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        delta = (date.today() - d).days
        if delta == 0: return "今天"
        if delta == 1: return "昨天"
        if delta < 7: return f"{delta}天前"
        if delta < 30: return f"{delta // 7}周前"
        if delta < 365: return f"{delta // 30}个月前"
        return f"{delta // 365}年前"
    except Exception:
        return date_str[:10]

slug = ''.join(c if c.isalnum() else '-' for c in pwd)
project_dir = os.path.join(projects_dir, slug)
index_file = os.path.join(project_dir, "sessions-index.json")

# 策略1：读 sessions-index.json，记录已索引的 session ID
index_ids = set()
if os.path.exists(index_file):
    try:
        with open(index_file) as f:
            data = json.load(f)
        for e in data.get("entries", []):
            if e.get("projectPath", pwd) != pwd:
                continue
            sid = e.get("sessionId", "")
            if not sid:
                continue
            index_ids.add(sid)
            sessions[sid] = {
                "id": sid[:8],
                "sort_key": e.get("modified", ""),
                "date": relative_date(e.get("modified", "")[:10]),
                "summary": e.get("summary") or e.get("firstPrompt") or "(no summary)",
                "branch": e.get("gitBranch", ""),
            }
    except Exception:
        pass

# 策略2：扫描 .jsonl 文件，补充 index 中没有的会话（最多读 200 行）
if os.path.isdir(project_dir):
    for fname in os.listdir(project_dir):
        if not fname.endswith(".jsonl"):
            continue
        sid_full = fname[:-6]  # 去掉 .jsonl 后缀即为 UUID
        if sid_full in index_ids:
            continue  # 已在 index 中，跳过
        fpath = os.path.join(project_dir, fname)
        mtime = os.path.getmtime(fpath)
        first_text = ""
        try:
            with open(fpath) as f:
                for i, line in enumerate(f):
                    if i >= 200:
                        break
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if obj.get("type") == "summary":
                        first_text = obj.get("summary", "")
                        break
                    if not first_text and obj.get("type") == "user":
                        content = obj.get("message", {}).get("content", "")
                        if isinstance(content, list):
                            first_text = next((c.get("text","") for c in content if c.get("type")=="text"), "")
                        else:
                            first_text = str(content)
        except Exception:
            pass
        if first_text:
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            sessions[sid_full] = {
                "id": sid_full[:8],
                "sort_key": datetime.fromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%S"),
                "date": relative_date(mtime_str),
                "summary": first_text.strip(),
                "branch": "",
            }

# 策略3（兜底）：slug 目录不存在时才全扫描，用 originalPath 精确匹配
if not sessions and not os.path.isdir(project_dir) and os.path.isdir(projects_dir):
    for s in os.listdir(projects_dir):
        idx = os.path.join(projects_dir, s, "sessions-index.json")
        if not os.path.exists(idx):
            continue
        try:
            with open(idx) as f:
                data = json.load(f)
        except Exception:
            continue
        entries = data.get("entries", [])
        original = data.get("originalPath", "")
        if original != pwd and not any(e.get("projectPath") == pwd for e in entries):
            continue
        for e in entries:
            if e.get("projectPath", pwd) != pwd:
                continue
            sid = e.get("sessionId", "")
            if not sid or sid in sessions:
                continue
            sessions[sid] = {
                "id": sid[:8],
                "sort_key": e.get("modified", ""),
                "date": relative_date(e.get("modified", "")[:10]),
                "summary": e.get("summary") or e.get("firstPrompt") or "(no summary)",
                "branch": e.get("gitBranch", ""),
            }

if not sessions:
    print("NO_SESSIONS")
else:
    all_sessions = sorted(sessions.values(), key=lambda x: x["sort_key"], reverse=True)
    total = len(all_sessions)
    for i, s in enumerate(all_sessions[:10], 1):
        branch = f" [{s['branch']}]" if s['branch'] else ""
        summary = s['summary'][:45] + "..." if len(s['summary']) > 45 else s['summary']
        print(f"{i}. [{s['date']}]{branch} {summary}")
        print(f"   claude --resume {s['id']}")
    if total > 10:
        print(f"（共 {total} 条，显示最近 10 条）")
PYEOF
```

**Step 2：展示结果**

- 若输出 `NO_SESSIONS`：回复"当前目录没有历史会话记录。"
- 否则在标题 `📋 历史会话（当前目录）` 后，**原样**输出脚本内容，不要改变格式、不要转成表格、不要省略任何行。
  每条会话是两行：第一行是摘要，第二行是 `claude --resume <id>`，两行都必须展示。
