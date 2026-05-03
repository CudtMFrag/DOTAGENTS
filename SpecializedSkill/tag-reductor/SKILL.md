---
name: tag-reductor
description: Reductionist content tagging - extract flat, short tags from article/bookmark/chat collections, generate word cloud and co-occurrence graph visualizations. Use when the user wants to "analyze tags", "归类标签", "打标签", "标签归约", or distill a personal tag taxonomy from any collection of saved content.
---

# Tag Reductor

Reduces a collection of articles, notes, bookmarks, or chat logs into a flat, composable tag vocabulary. The core method is **reductionist decomposition**: start with broad themes, then split them by internal differences until each tag describes a specific, meaningful thread.

Tags are **additive descriptors**. They coexist and combine freely rather than forming a mutually exclusive classification tree.

## Execution Requirements

This skill works best when the runtime has:

- **Multi-agent capability** for parallel deep reading across batches.
- **Configured cheaper models** for batch analysis. Deep reading is token-heavy and usually does not require the strongest model for every batch.
- **A capable synthesis model** for the final reduction step. The merge/deduplication pass requires enough judgment to preserve established terms, split weak compounds, and avoid keyword noise.
- **Embedding support** if clustering or backfill is requested. Use OpenAI embeddings when credentials are available, or local `sentence-transformers` models when offline.

If the current environment does not allow sub-agents, or the user has not explicitly authorized delegation, process batches sequentially in the current agent. Do not spawn sub-agents unless the active system rules and the user's request allow it.

## Architecture

This is a general-purpose skill. It provides the methodology and pipeline. It does not ship with pre-built tag vocabularies or platform-specific parsers. Users can layer a personal skill on top that bundles their own content and vocabulary.

## High-Level Pipeline

1. **Parse** - extract readable content from whatever files the user provides. The model figures out the format.
2. **Survey** - present a landscape summary: how many items, what broad topics appear, and any existing tags found.
3. **Cluster** - group articles into rough categories using embeddings and clustering, or an AI scan of titles when that fits the content better.
4. **Deep read** - read batches within each category and perform reductionist decomposition. Use sub-agents only when the environment and user authorization allow it; otherwise process batches sequentially.
5. **Reduce** - merge all batch outputs into a single, deduplicated tag vocabulary. Validate against the iron rules. **Deliver `tag_vocabulary.json`** as the primary output. Stop here if the user only needs the tag list.
6. **Backfill** - optional. Use the vocabulary from Step 5 plus embedding similarity to assign tags to all articles. Deliver `tag_mapping.json`. Skip this step if the user plans to apply tags in their own tools.
7. **Visualize** - optional. Generate a word cloud and co-occurrence graph for quick inspection.

## Core: Reductionist Decomposition

The central operation is **splitting**. Within a rough category, ask: "How are these articles actually different from each other?" Name each distinction as a tag. Repeat until each tag captures a specific, meaningful thread.

Do not just extract keywords that appear in the text. A tag describes what the article is **about**.

## Tag Rules

### Iron Rules

1. **Flat** - no nesting, no hierarchy. Slash-separated paths must be split into separate tags.
2. **Max 2 words** - at most two words per tag, in whatever language the content is in.
3. **Additive** - one article can have many tags; tags coexist and do not compete.
4. **Naming** - a tag describes what the article is about, not what words happen to appear in it.

### Two Dimensions, Merged Flat

- **Domain tags**: what field, technology, or domain does this belong to?
- **Topic tags**: what specific subject, angle, or question does it address?

Both dimensions merge into one flat tag list per article.

### Split Judgment

- **Verb phrases** -> split, for example "learning english" -> "learning", "english".
- **Temporary combinations** -> split, for example "article collection" -> "article", "collection".
- **Professional or established terms** -> keep intact, for example "machine learning", "knowledge management", "independent development".

**The test**: after splitting, can each part still independently describe this specific article? If the split parts would reliably land on unrelated articles, the original term is indivisible; keep it.

## Batch Prompt Template

Use this template for deep reading. Append the batch of articles.

```markdown
You are a reductionist tag analyzer. Read the following batch of articles, identify internal differences between them, and produce tags.

## Rules
- Tags are flat, max 2 words, and additive.
- Output both domain tags and topic tags.
- A tag describes what the article IS ABOUT, not what words appear in it.
- Output tags as JSON arrays so multi-word tags remain intact.

## Split judgment
- Verb phrases -> split, for example "learning english" -> "learning", "english".
- Temporary combinations -> split, for example "article collection" -> "article", "collection".
- Professional or established terms -> keep intact, for example "machine learning", "knowledge management", "independent development".
- Test: after splitting, can each part still independently describe this specific article? If the split parts would reliably land on unrelated articles, the original term is indivisible; keep it.

## Output per article
{"title": "...", "tags": ["tag one", "tag two", "tag three"]}

## After all articles
Summarize internal differences you found within this batch.
```

## Data Contracts

Use JSON arrays for all tag lists. Do not serialize tags as a space-separated string, because valid tags can contain spaces.

### `tag_vocabulary.json`

```json
{
  "meta": {"created": "2026-04-30", "source_count": 300},
  "tags": ["tag one", "tag two", "tag three"]
}
```

This is the **primary output**. The user can take this file and use it anywhere.

### `tag_mapping.json`

```json
[
  {"title": "...", "content": "...", "tags": ["tag one", "tag two"]},
  {"title": "...", "content": "...", "tags": []}
]
```

## Optional: Embedding Backfill

If the user wants the agent to assign tags to every article, use embedding similarity. This step consumes `tag_vocabulary.json` and produces `tag_mapping.json`.

Skip this step if the user prefers to apply tags themselves using their own tools.

### Model Selection

Ask the user which embedding approach they prefer when the choice materially affects cost, privacy, or setup. Otherwise default by environment:

| Option | Model | Requires | Best for |
|--------|-------|----------|----------|
| Remote | `text-embedding-3-small` | OpenAI API key | Mixed Chinese/English content, higher accuracy |
| Local English | `all-MiniLM-L6-v2` | `sentence-transformers` | Free, offline, English-dominant content |
| Local Chinese | `BAAI/bge-small-zh` | `sentence-transformers` | Chinese-dominant content |

Default to remote if credentials are available and remote calls are acceptable. Otherwise choose a local model based on language.

### Algorithm

```python
vocab = load_json("tag_vocabulary.json")
tags = vocab["tags"]

prototypes = {}
for tag in tags:
    articles_with_tag = [a for a in tagged_articles if tag in a["tags"]]
    embeddings = embed([a["title"] + " " + a.get("content", "") for a in articles_with_tag])
    prototypes[tag] = mean(embeddings, axis=0)

for article in untagged_articles:
    article_emb = embed(article["title"] + " " + article.get("content", ""))
    scores = {tag: cosine_sim(article_emb, proto) for tag, proto in prototypes.items()}
    article["tags"] = [tag for tag, score in top_k(scores, K) if score > threshold]

save_json("tag_mapping.json", all_articles)
```

A bundled script, `scripts/backfill.py`, provides a reference implementation.

## Strategy Notes

- **Use cheaper batch models when allowed** - batch analysis is mostly classification and decomposition, but still requires enough judgment to avoid keyword extraction.
- **Reserve the strongest model for reduction** - the final vocabulary merge is the highest-judgment step.
- **Respect the active agent runtime** - use sub-agents only when permitted; otherwise process batches sequentially.
- **Visualization is a bonus** - the word cloud and co-occurrence graph are for quick human inspection, not the main deliverable. A bundled script, `scripts/viz.py`, can generate this from `tag_mapping.json`.

## Bundled Scripts

| Script | Purpose |
|--------|---------|
| `scripts/cluster.py` | Embed and cluster articles |
| `scripts/backfill.py` | Embedding-based tag assignment for remaining articles |
| `scripts/viz.py` | Generate D3 word cloud and force graph HTML from tag data |
