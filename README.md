# skillHome

一个 [Claude Code](https://claude.ai/code) Skills 的集合，用于增强 AI 辅助开发的能力。

## 安装方法

### 方式一：下载 zip（推荐）

1. 进入对应 skill 目录，下载 `.zip` 文件
2. 解压，将解压出的目录放入 `~/.claude/skills/`
3. 重启 Claude Code 即可使用

```bash
# 以 my-god 为例
unzip my-god.zip -d ~/.claude/skills/
```

### 方式二：克隆整个仓库

```bash
git clone https://github.com/Pandaoray/skillHome.git
cp -r skillHome/my-god ~/.claude/skills/
cp -r skillHome/agents-book ~/.claude/skills/
cp -r skillHome/podcast-chat ~/.claude/skills/
```

---

## Skills 列表

### [agents-book](./agents-book/)

为代码项目自动生成 `AGENTS.md` 文档体系，让 AI 在不读完所有源码的前提下就能理解项目结构、找到修改入口、预见潜在风险。

**触发方式**：`我想为这个项目生成 AGENTS.md 文档体系，请使用 agents-book skill`

---

### [my-god](./my-god/)

Human-assisted AI 编程工作流。通过多 Agent 协作，将一行需求转化为完整的开发 PR，覆盖需求澄清、架构设计、并行开发、代码审查等全流程。

**触发方式**：
```
/myGod 为用户列表页添加分页和搜索功能
/myGod quick 修改按钮颜色
/myGod hotfix 修复登录接口 500 错误
```

---

### [podcast-chat](./podcast-chat/)

转录播客并与内容对话。支持 Apple Podcasts 和小宇宙，自动完成音频下载、Whisper 转录、结构化摘要，对话时附带时间戳引用。

**依赖**：
```bash
brew install ffmpeg
pip install faster-whisper
```

**触发方式**：粘贴播客链接，加上"转录"、"讲了什么"、"聊聊"等关键词即可。

---

## 了解更多

每个 skill 的详细介绍见 [Skill Notes](https://pandaoray.github.io/skills/)。
