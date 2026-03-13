#!/usr/bin/env python3
"""
history-session: List historical Claude Code sessions for the current directory.

Usage: python3 history_session.py <project_path>
"""

import json
import os
import sys
from datetime import datetime, date


def relative_date(date_str):
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        delta = (date.today() - d).days
        if delta == 0:
            return "今天"
        if delta == 1:
            return "昨天"
        if delta < 7:
            return f"{delta}天前"
        if delta < 30:
            return f"{delta // 7}周前"
        if delta < 365:
            return f"{delta // 30}个月前"
        return f"{delta // 365}年前"
    except Exception:
        return date_str[:10]


def read_index(index_file, pwd):
    """Read sessions-index.json, return (sessions dict, index_ids set)."""
    sessions = {}
    index_ids = set()
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
    return sessions, index_ids


def read_jsonl(fpath, mtime):
    """Extract first meaningful text from a .jsonl session file (max 200 lines)."""
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
                    return obj.get("summary", "")
                if not first_text and obj.get("type") == "user":
                    content = obj.get("message", {}).get("content", "")
                    if isinstance(content, list):
                        first_text = next(
                            (c.get("text", "") for c in content if c.get("type") == "text"),
                            "",
                        )
                    else:
                        first_text = str(content)
    except Exception:
        pass
    return first_text


def scan_jsonl(project_dir, index_ids, pwd):
    """Scan .jsonl files in project_dir, skip sessions already in index_ids."""
    sessions = {}
    for fname in os.listdir(project_dir):
        if not fname.endswith(".jsonl"):
            continue
        sid_full = fname[:-6]  # UUID is the filename without .jsonl
        if sid_full in index_ids:
            continue
        fpath = os.path.join(project_dir, fname)
        mtime = os.path.getmtime(fpath)
        first_text = read_jsonl(fpath, mtime)
        if first_text:
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            sessions[sid_full] = {
                "id": sid_full[:8],
                "sort_key": datetime.fromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%S"),
                "date": relative_date(mtime_str),
                "summary": first_text.strip(),
                "branch": "",
            }
    return sessions


def full_scan(projects_dir, pwd):
    """Fallback: scan all project dirs and match by originalPath."""
    sessions = {}
    for slug in os.listdir(projects_dir):
        idx = os.path.join(projects_dir, slug, "sessions-index.json")
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
    return sessions


def main():
    pwd = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    projects_dir = os.path.join(os.path.expanduser("~"), ".claude", "projects")

    slug = "".join(c if c.isalnum() else "-" for c in pwd)
    project_dir = os.path.join(projects_dir, slug)
    index_file = os.path.join(project_dir, "sessions-index.json")

    sessions = {}

    # Strategy 1: Read sessions-index.json (O(1) lookup)
    if os.path.exists(index_file):
        s, index_ids = read_index(index_file, pwd)
        sessions.update(s)
    else:
        index_ids = set()

    # Strategy 2: Supplement with .jsonl files not in index
    if os.path.isdir(project_dir):
        sessions.update(scan_jsonl(project_dir, index_ids, pwd))

    # Strategy 3: Full scan fallback (slug dir doesn't exist at all)
    if not sessions and not os.path.isdir(project_dir) and os.path.isdir(projects_dir):
        sessions.update(full_scan(projects_dir, pwd))

    if not sessions:
        print("NO_SESSIONS")
        return

    all_sessions = sorted(sessions.values(), key=lambda x: x["sort_key"], reverse=True)
    total = len(all_sessions)
    for i, s in enumerate(all_sessions[:10], 1):
        branch = f" [{s['branch']}]" if s["branch"] else ""
        summary = s["summary"][:45] + "..." if len(s["summary"]) > 45 else s["summary"]
        print(f"{i}. [{s['date']}]{branch} {summary}")
        print(f"   claude --resume {s['id']}")
    if total > 10:
        print(f"（共 {total} 条，显示最近 10 条）")


if __name__ == "__main__":
    main()
