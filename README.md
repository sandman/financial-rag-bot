### Financial RAG Bot

Lightweight Retrieval-Augmented Generation (RAG) bot for answering questions over your financial PDFs. Uses hybrid search (FAISS + BM25) and an LLM to produce answers with inline citations.

### Quickstart

1. Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here   # or create a .env with OPENAI_API_KEY=...
```

2. Add documents

- Drop PDFs into `data/raw/`.

3. Ingest and index

```bash
python -m ingestion.parse_docs     # builds data/processed/docs.jsonl
python -m ingestion.build_index    # builds FAISS/BM25 in data/index/
```

4. Run the API

```bash
uvicorn app:app --reload
```

5. Ask a question

```bash
curl 'http://127.0.0.1:8000/chat?q=What is the fund\'s expense ratio?'
```

### How it works

- **Ingestion**: `ingestion/parse_docs.py` extracts page text from PDFs → `data/processed/docs.jsonl`.
- **Indexing**: `ingestion/build_index.py` creates embeddings (all-mpnet-base-v2) → FAISS + BM25.
- **Retrieval**: `retrieval/retriever.py` performs hybrid search to fetch top passages.
- **Orchestration**: `llm/orchestrator.py` calls the LLM with context; answers cite `[doc p.page]` or say "Not found in documents".

### Notes

- Requires Python 3.12+.
- Index artifacts are stored in `data/index/`.
- For macOS/Python 3.12, the index build runs in a safe, single-process mode (already handled in the scripts).
