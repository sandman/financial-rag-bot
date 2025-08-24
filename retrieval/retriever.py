# retrieval/retriever.py
import os
import json
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import torch

# Disable parallel tokenizers and limit thread usage to avoid semaphore leaks/warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
torch.set_num_threads(1)

INDEX_DIR = Path("data/index")

# Load models + indexes
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cpu")
faiss_index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
docs = json.load(open(INDEX_DIR / "docs.json"))
bm25 = pickle.load(open(INDEX_DIR / "bm25.pkl", "rb"))


def reload_indexes():
    global faiss_index, docs, bm25
    faiss_index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
    docs = json.load(open(INDEX_DIR / "docs.json"))
    bm25 = pickle.load(open(INDEX_DIR / "bm25.pkl", "rb"))
    return True


def safe_encode(texts, batch_size=8):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = embedder.encode(
            batch,
            convert_to_numpy=True,
            num_workers=0,
            show_progress_bar=False,
        )
        all_embeddings.append(emb)
    return np.vstack(all_embeddings)


def hybrid_search(query, top_k=5):
    # Semantic search
    q_emb = safe_encode([query])
    D, indices = faiss_index.search(q_emb, top_k)
    semantic_hits = [(docs[i], float(D[0][j])) for j, i in enumerate(indices[0])]

    # BM25 search
    bm25_scores = bm25.get_scores(query.split())
    bm25_top = np.argsort(bm25_scores)[::-1][:top_k]
    bm25_hits = [(docs[i], float(bm25_scores[i])) for i in bm25_top]

    # Merge (naive union; could do reciprocal rank fusion later)
    hits = semantic_hits + bm25_hits
    hits = sorted(hits, key=lambda x: x[1], reverse=True)[:top_k]

    return hits
