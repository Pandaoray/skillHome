---
name: podcast-chat
description: "Transcribe and discuss podcast episodes from Apple Podcasts or Xiaoyuzhou (小宇宙) URLs. Use when the user provides a podcast episode link and wants to get the full transcript from audio, understand the main content and key points, or have a deep conversation about the episode. Handles the full pipeline automatically: URL → audio download → Whisper transcription → structured summary → interactive discussion. Triggers on any Apple Podcasts URL (podcasts.apple.com) or Xiaoyuzhou URL (xiaoyuzhoufm.com) combined with words like 转录, 内容, 讲了什么, 分析, 对谈, 聊聊, transcript, summarize."
---

# Podcast Chat

Transcribe podcast episodes and engage in conversation about their content.

## Supported Platforms

- **Apple Podcasts**: `https://podcasts.apple.com/...?i={episode_id}`
- **Xiaoyuzhou (小宇宙)**: `https://www.xiaoyuzhoufm.com/episode/{id}`

> Apple Podcasts works for recent episodes (RSS feed) and latest ~200 via iTunes API. For older or special episodes (SP series), use the Xiaoyuzhou URL instead.

## Workflow

### Step 0: Check Transcript Cache

Compute a cache key from the URL and check if transcript already exists:

```bash
CACHE_KEY=$(python3 -c "import hashlib,sys; print(hashlib.md5(sys.argv[1].encode()).hexdigest()[:12])" "<URL>")
CACHE_DIR=~/.claude/memory/podcasts
mkdir -p $CACHE_DIR
CACHE_FILE=$CACHE_DIR/$CACHE_KEY.txt
ls $CACHE_FILE 2>/dev/null && echo "CACHE_HIT" || echo "CACHE_MISS"
```

**Cache hit**: Skip Steps 1–4, read transcript from `$CACHE_FILE`, proceed to Step 5.

**Cache miss**: Continue with Steps 1–4.

### Step 1: Extract Audio URL

```bash
python3 ~/.claude/skills/podcast-chat/scripts/get_audio_url.py "<URL>"
```

If it fails, show this message and ask the user for the Xiaoyuzhou URL:

> 无法通过 iTunes API 获取该期音频（可能是较早期或 SP 系列）。
> 请提供该期的**小宇宙 URL**（格式：`https://www.xiaoyuzhoufm.com/episode/...`），可在小宇宙 App 分享或网页版找到。

### Step 2: Download Audio

Use `$CACHE_KEY` in the filename to avoid collisions between episodes:

```bash
AUDIO_FILE=/tmp/podcast_$CACHE_KEY.m4a
curl -L -o $AUDIO_FILE "<AUDIO_URL>"
```

After download, immediately check duration:

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 $AUDIO_FILE 2>/dev/null || \
  ffprobe -i $AUDIO_FILE 2>&1 | grep -oP '(?<=Duration: )\d+:\d+:\d+'
```

### Step 3: Choose Language and Model

**Language detection rules:**
- `xiaoyuzhoufm.com` URL → `zh`
- Apple Podcasts + podcast name clearly Chinese → `zh`
- Apple Podcasts + podcast name clearly English → `en`
- Unclear (bilingual title, mixed content) → **ask the user**

**Model selection — check backend first:**

```bash
python3 -c "import faster_whisper; print('faster-whisper available')" 2>/dev/null || \
  python3 -c "import whisper; print('openai-whisper available')" 2>/dev/null || \
  echo "NONE"
```

- `faster-whisper available` → 直接使用
- `openai-whisper available` → 提示用户："检测到 openai-whisper，建议安装 faster-whisper（速度约快 4 倍，`pip install faster-whisper`）。是否现在安装？"
  - 是 → `pip install faster-whisper`，安装完后使用 faster-whisper
  - 否 → 继续使用 openai-whisper
- `NONE` → 必须安装，告知用户："未检测到转录后端，正在安装 faster-whisper..." 然后执行 `pip install faster-whisper`

Based on audio duration and language, recommend a model:

| Condition | Recommended | Reason |
|-----------|------------|--------|
| Chinese podcast, any length | `medium` | Noticeably better accuracy for Chinese |
| English podcast, > 40 min | `small` | Good enough accuracy, ~3× faster |
| English podcast, ≤ 40 min | `medium` | Accurate and still fast |

Tell the user the estimated time before starting:

> 音频时长约 {X} 分钟（`faster-whisper` 可用时速度约为原版 4 倍）。
> 推荐：**{model}**（{reason}）。是否使用，还是切换另一个？

If user confirms (or says nothing within the conversation turn), proceed.

### Step 4: Transcribe

```bash
TRANSCRIPT_FILE=/tmp/transcript_$CACHE_KEY.txt
python3 ~/.claude/skills/podcast-chat/scripts/transcribe.py \
  $AUDIO_FILE --model <model> --language <lang> --output $TRANSCRIPT_FILE \
  > /tmp/whisper_progress.log 2>&1
```

Run as a background task. To check progress at any time:

```bash
tail -5 /tmp/whisper_progress.log
```

After transcription completes, save to cache:

```bash
cp $TRANSCRIPT_FILE $CACHE_FILE
```

### Step 5: Ask About Saving

Ask the user: "转录完成！是否需要将文本保存为文件？（默认不保存）"

Options if yes:
- **TXT**：保存为纯文本 `{cwd}/{episode_title}.txt`
- **Markdown**：按话题分段，带章节标题，保存为 `{cwd}/{episode_title}.md`

### Step 6: Present Structured Summary

```
## 📻 {Episode Title}
**平台** | **时长** | **主播**

### 核心主题
[1-2句概括]

### 主要观点
1. ...
2. ...（3-7条，每条附简短说明）

### 值得关注的细节
[有意思的细节或金句，附大致时间位置，如"约第 35 分钟"]

---
想深入探讨哪个方向？
```

### Step 7: Engage in Conversation

Answer follow-up questions by referencing transcript content.

**Timestamp references**: The transcript contains `[Xs]` prefixes (seconds). When citing specific content, convert to human-readable form:
- `[2134.5s]` → "约第 **35 分钟**"
- `[312.0s]` → "约第 **5 分钟**"

Quote specific passages when relevant, always include the approximate time position so the user can jump to that part in the original audio.
