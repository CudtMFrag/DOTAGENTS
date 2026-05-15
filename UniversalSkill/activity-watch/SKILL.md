---
name: activity-watch
description: >
  ActivityWatch time tracking assistant. Help users categorize activities, analyze time usage, write queries for the Web UI query editor, and find focus patterns. Covers the query language (query_bucket, flood, merge_events_by_keys, categorize, filter_keyvals, filter_period_intersect, sum_durations, etc.), categorization rules (regex + select_keys), the canonical desktop query pattern (window + AFK + browser), and common analysis recipes. Use when the user asks about ActivityWatch, wants to know where their time went, set up categories, write/modify queries, or understand their productivity patterns.
---

# ActivityWatch

ActivityWatch records what you do on your computer. Watchers collect raw events (active window, AFK status, browser tabs), stored in buckets. The Web UI at `localhost:5600` lets you explore data via a query editor, timeline view, and category system.

## Architecture

```
aw-qt (tray manager)
  ├── aw-server (REST API on :5600, serves Web UI)
  ├── aw-watcher-window  →  bucket: aw-watcher-window_<hostname>
  ├── aw-watcher-afk     →  bucket: aw-watcher-afk_<hostname>
  └── aw-watcher-web     →  bucket: aw-watcher-web_<hostname>  (browser extension)
```

Each event has `timestamp`, `duration` (usually 0 — heartbeats), and `data` (dict with fields like `app`, `title`, `url`, `status`).

The query engine (`aw_query`) is a simple scripting language: assign variables, chain transforms, return results. The standard pattern — called the canonical query — merges window events with AFK events to filter out idle time, then applies categorization.

## Quick start: verify everything is working

Open `http://localhost:5600` in a browser. If unreachable, ActivityWatch isn't running.

Windows (Scoop): `Start-Process "D:\Scoop\shims\aw-qt.exe" -WindowStyle Hidden`
Linux/macOS: run `aw-qt` (or launch from app menu).

In the Web UI:
- **Activity tab** → query editor + summary view (app usage, category breakdown, browser URLs)
- **Timeline tab** → visual timeline of all events
- **Settings** → manage categories

## Categorization

Categories let you group raw events into meaningful buckets like "Work", "Entertainment", "Learning". ActivityWatch uses a tree structure — nested categories work like folders.

### Rule format

Each category has a list of rules. A rule matches an event if its `regex` pattern matches any value in the event's `data` dict (or only the keys listed in `select_keys`).

```json
{
  "Work": {
    "children": {
      "Coding": {
        "rules": [
          {"regex": "Code\\.exe|idea64\\.exe|WindowsTerminal\\.exe", "type": "regex"},
          {"regex": ".*\\.py$|.*\\.rs$|.*\\.ts$", "type": "regex", "select_keys": ["title"]}
        ]
      },
      "Communication": {
        "rules": [
          {"regex": "Slack|slack\\.exe|Teams\\.exe", "type": "regex"},
          {"regex": "mail\\.google\\.com|outlook\\.office\\.com", "type": "regex"}
        ]
      }
    }
  },
  "Entertainment": {
    "children": {
      "Social Media": {
        "rules": [{"regex": "twitter\\.com|reddit\\.com|weibo\\.com|bilibili\\.com", "type": "regex"}]
      },
      "Video": {
        "rules": [{"regex": "youtube\\.com|netflix\\.com|bilibili\\.com/video", "type": "regex"}]
      }
    }
  }
}
```

Key details from `aw_transform/classify.py`:
- `regex` — Python regex, compiled with `re.UNICODE`. If `ignore_case: true` is set, also `re.IGNORECASE`.
- `select_keys` (optional) — list of field names to check. Without it, ALL values in `event.data` are checked. Use `["app"]` to match only the process name, `["url"]` for browser URLs, `["title"]` for window titles.
- Deepest matching category wins. If `["Work", "Coding"]` and `["Work"]` both match, the event gets `["Work", "Coding"]`.

### How to design categories from scratch

Don't guess. Pull the user's actual top apps:

1. Open Web UI → Activity tab, set date range to "last 7 days"
2. Look at the "Top apps" panel — these are the user's most-used applications
3. For each top app, ask the user: which category does this belong to?
4. Build rules from their answers, with concrete regex patterns matching their actual app names

### Where categories are stored

Categories live in server settings, editable from the Web UI (Settings page) or via the settings file:
- Windows: `%LOCALAPPDATA%\activitywatch\activitywatch\aw-server\settings.json`
- Linux: `~/.config/activitywatch/aw-server/settings.json`

### Suggestion from raw data

If the user has no categories yet, the "Suggest categories" pattern helps discover what's worth categorizing. In the query editor:

```
events = query_bucket(find_bucket("aw-watcher-window_"));
events = flood(events);
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = merge_events_by_keys(events, ["app"]);
events = sort_by_duration(events);
RETURN = limit_events(events, 20);
```

This returns the top 20 apps by duration (filtered to active time). Present these to the user and ask them to classify each.

## The query language

All queries run in the Web UI query editor (Activity tab). Statements end with `;`, results are returned via `RETURN = ...;`.

### Available functions (from `aw_query/functions.py`)

**Getting data:**
- `query_bucket(bucket_name)` — get all events from a bucket for the current time range
- `find_bucket(filter_str)` — find a bucket by partial name match (e.g., `find_bucket("aw-watcher-window_")`)

**Filtering:**
- `filter_keyvals(events, key, vals)` — keep events where `key` value is in `vals`. Example: `filter_keyvals(events, "app", ["Code.exe", "WindowsTerminal.exe"])`
- `exclude_keyvals(events, key, vals)` — remove events where `key` value is in `vals`. Example: `exclude_keyvals(events, "app", ["msedge.exe"])`
- `filter_keyvals_regex(events, key, regex)` — keep events where `key` value matches regex
- `filter_period_intersect(events, filter_events)` — keep only events that overlap in time with filter_events. The classic use: intersect window events with not-afk events to remove idle time.

**Merging:**
- `merge_events_by_keys(events, keys)` — combine adjacent events that share the same values for the given keys. This turns heartbeat events (0 duration) into spans with real durations. Example: `merge_events_by_keys(events, ["app"])` groups by app only; `merge_events_by_keys(events, ["app", "title"])` groups by app+title.
- `flood(events)` — fill gaps between events (prevents tiny breaks from fragmenting merged spans). Almost always used before merge_events_by_keys.
- `chunk_events_by_key(events, key)` — split events where `key` value changes
- `period_union(events1, events2)` — union of two event lists

**Classifying:**
- `categorize(events, classes)` — add `$category` field to each event based on matching rules. `classes` is a list of `[category_path, rule_dict]` pairs. Example:
  ```
  events = categorize(events, [
      [["Work", "Coding"], {"regex": "Code\\.exe", "select_keys": ["app"]}],
      [["Work"], {"regex": "slack\\.exe|Teams\\.exe", "select_keys": ["app"]}],
  ]);
  ```
- `tag(events, classes)` — same as categorize but adds `$tags` field (can have multiple tags per event)

**Sorting & limiting:**
- `sort_by_timestamp(events)` — chronological order
- `sort_by_duration(events)` — longest duration first
- `limit_events(events, n)` — keep top N events

**Summarizing:**
- `sum_durations(events)` — total duration of all events
- `concat(events1, events2)` — combine two event lists
- `union_no_overlap(events1, events2)` — combine without overlapping segments

**Transform:**
- `split_url_events(events)` — parse URLs, add `$domain`, `$path`, `$protocol`, `$params` fields
- `simplify_window_titles(events, key)` — clean up window titles: removes `(2)` number prefixes, `●`/`*` bullets, FPS counters

### The canonical desktop query

This is the query the Web UI runs by default (from `aw_client/queries.py`). It's the standard template for answering "what did I do?":

```
events = flood(query_bucket(find_bucket("aw-watcher-window_")));
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = categorize(events, <your_categories_here>);
title_events = sort_by_duration(merge_events_by_keys(events, ["app", "title"]));
app_events = sort_by_duration(merge_events_by_keys(title_events, ["app"]));
cat_events = sort_by_duration(merge_events_by_keys(events, ["$category"]));
duration = sum_durations(events);
RETURN = {"app_events": app_events, "cat_events": cat_events, "duration": duration};
```

This is the foundation. Adapt it for specific questions.

## Common analysis recipes

### "How much time did I spend on X today?"

Replace X with an app name or category:

```
events = flood(query_bucket(find_bucket("aw-watcher-window_")));
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = filter_keyvals_regex(events, "app", "Code\\.exe");
duration = sum_durations(events);
RETURN = duration;
```

### "Break down today by category"

Requires categories to be set up first:

```
events = flood(query_bucket(find_bucket("aw-watcher-window_")));
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = categorize(events, [
    [["Work", "Coding"], {"regex": "Code\\.exe|idea64\\.exe", "select_keys": ["app"]}],
    [["Work", "Writing"], {"regex": "Obsidian\\.exe|Notion\\.exe", "select_keys": ["app"]}],
    [["Entertainment"], {"regex": "youtube\\.com|reddit\\.com", "select_keys": ["url"]}],
]);
events = merge_events_by_keys(events, ["$category"]);
events = sort_by_duration(events);
RETURN = events;
```

### "When am I most focused?"

Find long uninterrupted blocks on productive apps:

```
events = flood(query_bucket(find_bucket("aw-watcher-window_")));
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = filter_keyvals_regex(events, "app", "Code\\.exe|idea64\\.exe|WindowsTerminal\\.exe");
events = merge_events_by_keys(events, ["app"]);
events = sort_by_duration(events);
RETURN = limit_events(events, 10);
```

The longest merged events = deep work blocks.

### "Find distractions during work hours"

Cross-reference entertainment events against a work time window:

```
events = flood(query_bucket(find_bucket("aw-watcher-window_")));
events = filter_keyvals_regex(events, "app", "msedge\\.exe|chrome\\.exe|firefox\\.exe");
not_afk = flood(query_bucket(find_bucket("aw-watcher-afk_")));
not_afk = filter_keyvals(not_afk, "status", ["not-afk"]);
events = filter_period_intersect(events, not_afk);
events = split_url_events(events);
events = filter_keyvals_regex(events, "$domain", "twitter\\.com|reddit\\.com|youtube\\.com");
events = merge_events_by_keys(events, ["$domain"]);
events = sort_by_duration(events);
RETURN = events;
```

### "What's my computer time today vs this week?"

```
events = query_bucket(find_bucket("aw-watcher-afk_"));
not_afk = filter_keyvals(events, "status", ["not-afk"]);
duration = sum_durations(not_afk);
RETURN = duration;
```

## Troubleshooting

**Web UI won't open / connection refused**: aw-qt not running. Start it (Windows Scoop: `Start-Process "D:\Scoop\shims\aw-qt.exe" -WindowStyle Hidden`, Linux: `aw-qt &`). Wait 3 seconds.

**Bucket not found**: check which watchers are actually running. aw-qt's autostart_modules in `aw-qt.toml` controls this.

**All events have 0 duration**: normal. ActivityWatch records heartbeat events (point-in-time), not spans. Use `flood()` + `merge_events_by_keys()` to turn them into duration spans.

**"Unknown" in window titles**: Wayland on Linux doesn't expose window titles. Use X11 or the macOS Swift strategy where possible.

**Categories not applying**: regex may be wrong. Test regex patterns independently (Python: `re.compile(r"pattern", re.IGNORECASE).search("test string")`). Remember regex matches against ANY value in event.data unless `select_keys` restricts it.

**Window titles show "excluded"**: checks `aw-watcher-window.toml` — `exclude_title = true` replaces all titles with "excluded". For focus analysis you want real titles.

**Browser extension not tracking**: install `aw-watcher-web` from the browser extension store (Chrome Web Store / Firefox Add-ons). It creates its own bucket independent of the window watcher.
