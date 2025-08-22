import json, pickle, faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from pathlib import Path

INDEX_DIR = Path("data/index")

embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
faiss_index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
docs = json.load(open(INDEX_DIR / "docs.json"))
bm25 = pickle.load(open(INDEX_DIR / "bm25.pkl", "rb"))


def hybrid_search(query, top_k=5):
    # semantic
    q_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = faiss_index.search(q_emb, top_k)
    semantic_hits = [(docs[i], float(D[0][j])) for j, i in enumerate(I[0])]

    # bm25
    bm25_scores = bm25.get_scores(query.split())
    bm25_top = np.argsort(bm25_scores)[::-1][:top_k]
    bm25_hits = [(docs[i], float(bm25_scores[i])) for i in bm25_top]

    # merge (naive, could do RRF)
    hits = semantic_hits + bm25_hits
    hits = sorted(hits, key=lambda x: x[1], reverse=True)[:top_k]

    return hits
