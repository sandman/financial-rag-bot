import torch
import numpy as np
from pathlib import Path
import json, pickle, faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# # Force safe multiprocessing mode on macOS/Python 3.12
# import torch.multiprocessing as mp

# mp.set_start_method("spawn", force=True)

torch.set_num_threads(1)

PROCESSED = Path("data/processed/docs.jsonl")
INDEX_DIR = Path("data/index")
INDEX_DIR.mkdir(exist_ok=True)


def build_index(batch_size: int = 8):
    print(f"Loading processed docs from {PROCESSED}...")

    docs, texts = [], []
    with open(PROCESSED) as f:
        for line in f:
            row = json.loads(line)
            docs.append(row)
            texts.append(row["text"])

    print(f"Loaded {len(docs)} documents")

    if not docs:
        raise RuntimeError("No documents found. Did you run parse_docs.py first?")

    # Load model (no multiprocessing)
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device="cpu")

    def encode_batches(texts, batch_size=batch_size):
        """Manual batching to avoid SentenceTransformer.encode() multiprocessing issues."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            with torch.no_grad():
                emb = model.encode(
                    batch, convert_to_numpy=True, batch_size=batch_size, num_workers=0
                )
            all_embeddings.append(emb)
            print(f"Encoded batch {i//batch_size+1}/{len(texts)//batch_size+1}")
        return np.vstack(all_embeddings)

    print("Encoding embeddings (safe mode)...")
    embeddings = encode_batches(texts, batch_size=batch_size)
    print("Finished encode, embeddings shape:", embeddings.shape)

    # Save FAISS index
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dim)
    faiss_index.add(embeddings)
    faiss.write_index(faiss_index, str(INDEX_DIR / "faiss.index"))
    print("Saved faiss.index")

    with open(INDEX_DIR / "docs.json", "w") as f:
        json.dump(docs, f)
    print("Saved docs.json")

    # Save BM25
    tokenized = [t.split() for t in texts]
    bm25 = BM25Okapi(tokenized)
    with open(INDEX_DIR / "bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)
    print("Saved bm25.pkl")

    print("Index build complete ✅")


if __name__ == "__main__":
    build_index()
