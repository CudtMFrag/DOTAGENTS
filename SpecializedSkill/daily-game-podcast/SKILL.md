---
name: daily-game-podcast
description: >
  Generate a daily Chinese gaming news podcast MP3 from Folo's Kite News 游戏 feed.
  Use when the user asks for 游戏播客, game podcast, 每日游戏新闻, gaming news audio,
  游戏语音播报, or wants to convert Folo gaming unread entries into a spoken podcast.
  Also use when user says 生成播客 or 转语音 after mentioning game news.
---

# Daily Game Podcast

Fetch unread entries from the Kite News 游戏 feed in Folo, compose a Chinese podcast script from them, convert to speech via xAI TTS, and mark entries as read.

## Prerequisites

- `XAI_API_KEY` environment variable set (xAI console → API keys)
- `npx folocli@latest` available (auto-installed via npx)
- Python 3 with `requests` library

## Fixed Configuration

- **Folo feed ID**: `204012564879785984` (Kite News 游戏 / Kagi News Gaming ZH-HANS)
- **TTS voice**: `rex` (professional, articulate — good for news)
- **TTS language**: `zh`
- **Output**: `kite-gaming-podcast.mp3` in the user's home directory

## Workflow

### Step 1: Fetch all unread entries

**Never add `--limit`.** Use `--unread-only` and paginate through ALL pages until `hasNext` is false.
Every single unread entry must be collected — no truncation, no subset.

```bash
# Page 1
npx --yes folocli@latest timeline --feed 204012564879785984 --unread-only
# Page 2+ (repeat until hasNext == false)
npx --yes folocli@latest timeline --feed 204012564879785984 --unread-only --cursor <nextCursor>
```

The response includes `title`, `description`, `publishedAt`, and `categories` for each entry.
**The `description` field is the primary news content** — Kite/Kagi has already synthesized the article
into a concise news blurb. This is your main writing source. Use it directly; do NOT discard it as "just a summary."

For entries where the description feels thin (< 100 chars), enrich by reading the full article:
```bash
npx --yes folocli@latest entry read <entryId>
```
Note: Kite News pages are often HTML templates with limited extracted text. The description field is usually
more useful than the readability output. Don't waste time reading every entry — sample 3-5 key ones at most.

**Deduplicate**: Kite News frequently emits near-duplicate entries for the same event from different source
articles. Before writing, scan all titles and descriptions; merge same-topic entries, keeping the richest details.

### Step 2: Compose the podcast script

Write a Chinese podcast script covering the fetched entries. Guidelines:

- **Tone**: conversational news anchor, enthusiastic but professional. Like a morning radio show.
- **Structure**: greeting → headlines grouped by theme → closing
- **Length**: aim for ~1000-2000 characters. Cover 10-15 most interesting stories, not every entry. Deduplicate aggressively.
- **Speech tags**: use xAI inline tags for expressiveness:
  - `[pause]` between story transitions
  - Use sparingly — one `[pause]` per section is enough
- **Grouping**: cluster related stories (same franchise, same company, same theme like "industry business" or "new releases")
- **Names**: keep game/company names in original language (e.g. "Switch 2", "Forza Horizon 6") — the TTS handles mixed zh/en well
- **Numbers**: write as digits or Chinese, both work. Prefer Chinese for small numbers (百分之二十), digits for large/dollar amounts (560 亿美元)
- **Date anchoring**: start with "今天是 2026 年 X 月 Y 日" (use actual current date)

Save the script to a temp file before TTS.

### Step 3: Generate speech

```bash
python <skill-dir>/scripts/tts.py --file <script-path> --output ~/kite-gaming-podcast.mp3
```

This script reads text, calls xAI `/v1/tts`, and saves the MP3. It requires `XAI_API_KEY` in the environment.

### Step 4: Mark entries as read

After successful TTS generation, mark all entries in this feed as read:

```bash
npx --yes folocli@latest entry mark-all-read --feed 204012564879785984
```

This ensures the next run only picks up genuinely new entries.

### Step 5: Report

Tell the user:
- How many new entries were covered
- The output file path and size
- Key headlines covered (3-5 bullet points)
- New date range covered

## Error Handling

- **Folo auth failure**: tell user to run `npx --yes folocli@latest login`
- **No unread entries**: tell user "Kite News 游戏暂无未读条目" and stop
- **XAI_API_KEY not set**: tell user to set the env var. Never ask for the key in chat — direct them to xAI console
- **TTS API error**: if 429, wait and retry once. If 400, check text length < 15000 chars. Other errors: report and stop

## Notes

- Folo feed ID is hardcoded — this skill is purpose-built for Kite News 游戏. Do not generalize.
- Podcast script is AI-generated each time — quality depends on entry descriptions. If entries are sparse, shorten rather than pad.
- TTS output is monaural MP3 at 44.1kHz / 192kbps — good for voice.
- Kite News frequently produces near-duplicate entries for the same event from different source articles. Always deduplicate before writing.
