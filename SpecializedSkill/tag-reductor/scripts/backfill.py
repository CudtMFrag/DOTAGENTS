"""
Backfill tags for untagged articles using embedding similarity against tagged prototypes.

Usage:
  uv run python backfill.py <tagged_items.json> <untagged_items.json> <tag_vocabulary.json> <output.json>
      [--model openai|local|local-zh] [--threshold 0.7] [--top-k 5]

Input and output use {"tags": ["multi word", "tag"]}. Legacy space-delimited
tag strings are accepted for compatibility, but cannot preserve multi-word tags.
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np


LOCAL_MODELS = {
    "local": "all-MiniLM-L6-v2",
    "local-zh": "BAAI/bge-small-zh",
}


def item_text(item):
    return (item.get("title", "") + " " + item.get("content", "")[:2000]).strip()


def normalize_tags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(tag).strip() for tag in value if str(tag).strip()]
    if isinstance(value, str):
        return [tag.strip() for tag in value.split() if tag.strip()]
    raise TypeError(f"Unsupported tags value: {value!r}")


def load_vocab(path):
    with open(path, encoding="utf-8") as f:
        vocab = json.load(f)
    tags = vocab.get("tags", [])
    if isinstance(tags, dict):
        tags = list(tags.keys())
    if not isinstance(tags, list):
        raise ValueError('tag_vocabulary.json must contain "tags" as a list')
    return [str(tag).strip() for tag in tags if str(tag).strip()]


def embed_openai(texts):
    from openai import OpenAI

    client = OpenAI()
    embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model="text-embedding-3-small", input=batch)
        embeddings.extend([d.embedding for d in resp.data])
        print(f"  embedded {min(i + batch_size, len(texts))}/{len(texts)}")
    return np.array(embeddings)


def embed_local(texts, model_name):
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    return np.array(model.encode(texts, show_progress_bar=True))


def embed(texts, model):
    if not texts:
        return np.empty((0, 0))
    if model == "openai":
        return embed_openai(texts)
    return embed_local(texts, LOCAL_MODELS[model])


def cosine_similarity(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def parse_args(argv):
    if len(argv) < 5:
        print(__doc__.strip())
        sys.exit(1)

    opts = {
        "tagged_path": argv[1],
        "untagged_path": argv[2],
        "vocab_path": argv[3],
        "output_path": argv[4],
        "model": "openai" if os.environ.get("OPENAI_API_KEY") else "local",
        "threshold": 0.7,
        "top_k": 5,
    }

    i = 5
    while i < len(argv):
        arg = argv[i]
        if arg == "--model" and i + 1 < len(argv):
            opts["model"] = argv[i + 1]
            i += 2
        elif arg == "--threshold" and i + 1 < len(argv):
            opts["threshold"] = float(argv[i + 1])
            i += 2
        elif arg == "--top-k" and i + 1 < len(argv):
            opts["top_k"] = int(argv[i + 1])
            i += 2
        else:
            raise SystemExit(f"Unknown or incomplete argument: {arg}")

    if opts["model"] not in {"openai", "local", "local-zh"}:
        raise SystemExit("--model must be one of: openai, local, local-zh")
    return opts


def main():
    opts = parse_args(sys.argv)

    with open(opts["tagged_path"], encoding="utf-8") as f:
        tagged = json.load(f)
    with open(opts["untagged_path"], encoding="utf-8") as f:
        untagged = json.load(f)

    tag_list = load_vocab(opts["vocab_path"])
    tag_set = set(tag_list)

    print(f"Tagged articles: {len(tagged)}, untagged: {len(untagged)}")
    print(f"Tags in vocabulary: {len(tag_list)}")
    print(f"Model: {opts['model']}, threshold: {opts['threshold']}, top-k: {opts['top_k']}")

    tag_articles = defaultdict(list)
    for item in tagged:
        item["tags"] = normalize_tags(item.get("tags"))
        text = item_text(item)
        for tag in item["tags"]:
            if tag in tag_set and text:
                tag_articles[tag].append(text)

    all_texts = []
    tag_text_indices = {}
    for tag in tag_list:
        texts = tag_articles.get(tag, [])
        if texts:
            tag_text_indices[tag] = (len(all_texts), len(all_texts) + len(texts))
            all_texts.extend(texts)

    untagged_texts = [item_text(item) for item in untagged]
    print(f"Embedding {len(all_texts)} prototype texts + {len(untagged_texts)} untagged articles...")
    all_embeddings = embed(all_texts + untagged_texts, opts["model"])

    tag_prototypes = {}
    for tag, (start, end) in tag_text_indices.items():
        tag_prototypes[tag] = np.mean(all_embeddings[start:end], axis=0)

    untagged_embs = all_embeddings[len(all_texts):]
    backfilled = 0
    for i, item in enumerate(untagged):
        if not tag_prototypes:
            item["tags"] = normalize_tags(item.get("tags"))
            item["count"] = len(item["tags"])
            continue

        sims = [(tag, cosine_similarity(untagged_embs[i], proto)) for tag, proto in tag_prototypes.items()]
        sims.sort(key=lambda x: -x[1])
        assigned = [tag for tag, sim in sims[:opts["top_k"]] if sim >= opts["threshold"]]
        item["tags"] = assigned
        item["count"] = len(assigned)
        if assigned:
            backfilled += 1

    print(f"Backfilled: {backfilled}/{len(untagged)}")

    with open(opts["output_path"], "w", encoding="utf-8") as f:
        json.dump(tagged + untagged, f, ensure_ascii=False, indent=2)
    print(f"Saved: {opts['output_path']}")


if __name__ == "__main__":
    main()
