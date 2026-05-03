"""
Embed articles and cluster them into rough categories.
Usage: uv run python cluster.py <parsed_items.json> <output.json> [--model openai|local|local-zh] [--n-clusters N]
"""
import json, sys, os
from collections import defaultdict

LOCAL_MODELS = {
    'local': 'all-MiniLM-L6-v2',
    'local-zh': 'BAAI/bge-small-zh',
}

def item_text(item):
    return (item.get('title', '') + ' ' + item.get('content', '')[:2000]).strip()

def cluster_with_openai(items, n_clusters):
    """Cluster using OpenAI embeddings. Requires OPENAI_API_KEY."""
    from openai import OpenAI
    client = OpenAI()

    texts = [item_text(item) for item in items]
    print(f'Embedding {len(texts)} articles with OpenAI text-embedding-3-small...')

    # Batch embed (max 2048 per batch)
    embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model='text-embedding-3-small', input=batch)
        embeddings.extend([d.embedding for d in resp.data])
        print(f'  {min(i + batch_size, len(texts))}/{len(texts)}')

    # K-means
    from sklearn.cluster import KMeans
    import numpy as np
    X = np.array(embeddings)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    return labels, texts

def cluster_local(items, n_clusters, model_name):
    """Cluster using local sentence-transformers."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)

    texts = [item_text(item) for item in items]
    print(f'Embedding {len(texts)} articles with local {model_name}...')
    embeddings = model.encode(texts, show_progress_bar=True)

    from sklearn.cluster import KMeans
    import numpy as np
    X = np.array(embeddings)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    return labels, texts

def extract_keywords(texts, labels, top_k=5):
    """Extract top TF-IDF keywords per cluster."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np

    # Simple tokenization for Chinese+English mixed text
    vectorizer = TfidfVectorizer(
        max_features=5000,
        token_pattern=r'(?u)\b\w+\b',
        stop_words=None
    )

    clusters = defaultdict(list)
    for i, label in enumerate(labels):
        clusters[int(label)].append(texts[i])

    keywords = {}
    for label, cluster_texts in clusters.items():
        try:
            tfidf = vectorizer.fit_transform(cluster_texts)
            feature_names = vectorizer.get_feature_names_out()
            summed = np.array(tfidf.sum(axis=0)).flatten()
            top_indices = summed.argsort()[-top_k:][::-1]
            keywords[int(label)] = [feature_names[i] for i in top_indices]
        except Exception:
            keywords[int(label)] = ['unknown']

    return keywords

def main():
    if len(sys.argv) < 3:
        print('Usage: uv run python cluster.py <parsed_items.json> <output.json> [--model openai|local|local-zh] [--n-clusters N]')
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Parse flags
    model = 'openai' if os.environ.get('OPENAI_API_KEY') else 'local'
    n_clusters = None
    for i, arg in enumerate(sys.argv):
        if arg == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
        if arg == '--n-clusters' and i + 1 < len(sys.argv):
            n_clusters = int(sys.argv[i + 1])

    with open(input_path, encoding='utf-8') as f:
        items = json.load(f)

    if not items:
        output = {'n_clusters': 0, 'model': model, 'clusters': {}}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        assigned_path = output_path.replace('.json', '_assigned.json')
        with open(assigned_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f'No items found. Empty outputs saved to: {output_path}, {assigned_path}')
        return

    if model not in {'openai', 'local', 'local-zh'}:
        raise SystemExit('--model must be one of: openai, local, local-zh')

    if n_clusters is None:
        n_clusters = max(3, int(len(items) ** 0.5))
    n_clusters = max(1, min(n_clusters, len(items)))
    print(f'Items: {len(items)}, target clusters: {n_clusters}, model: {model}')

    # Cluster
    if model == 'openai':
        labels, texts = cluster_with_openai(items, n_clusters)
    else:
        labels, texts = cluster_local(items, n_clusters, LOCAL_MODELS[model])

    # Extract keywords
    keywords = extract_keywords(texts, labels)

    # Build output
    clusters = defaultdict(list)
    for i, label in enumerate(labels):
        clusters[int(label)].append({
            'title': items[i]['title'],
            'content_snippet': items[i].get('content', '')[:200]
        })

    output = {
        'n_clusters': n_clusters,
        'model': model,
        'clusters': {}
    }
    for label in sorted(clusters.keys()):
        samples = clusters[label][:3]
        output['clusters'][str(label)] = {
            'keywords': keywords.get(label, []),
            'count': len(clusters[label]),
            'samples': [s['title'] for s in samples]
        }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Assign items back
    assigned_path = output_path.replace('.json', '_assigned.json')
    for i, item in enumerate(items):
        item['cluster'] = int(labels[i])
    with open(assigned_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f'\nClusters saved to: {output_path}')
    print(f'Assigned items saved to: {assigned_path}')
    for label in sorted(clusters.keys()):
        kw = keywords.get(label, [])
        count = len(clusters[label])
        print(f'  Cluster {label} ({count} items): {", ".join(kw[:5])}')

if __name__ == '__main__':
    main()
