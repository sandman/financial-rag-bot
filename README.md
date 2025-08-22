financial-rag-bot/
├── data/
│ ├── raw/ # Original PDFs, XLS, etc.
│ ├── processed/ # Markdown/JSON after parsing
│ └── index/ # SQLite DB + FAISS index
├── ingestion/
│ ├── parse_docs.py # PDF → Markdown/JSON
│ └── build_index.py # Build embeddings + BM25
├── retrieval/
│ ├── retriever.py # Hybrid retriever (BM25 + FAISS)
│ └── reranker.py # Cross-encoder reranker
├── llm/
│ ├── tools.py # Python/math/date tools
│ └── orchestrator.py # Query pipeline
├── app.py # FastAPI endpoint
├── requirements.txt
└── README.md
