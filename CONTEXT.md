## Financial RAG Bot Context

### 1. Scope & data hygiene (finance-specific)

- **Doc types**: PDFs (prospectuses, KIDs, factsheets), spreadsheets, policy docs, emails/FAQs
- **Parse & normalize**: extract to Markdown + structured JSON (tables kept as CSV/JSON; keep page numbers and section headings)
- **Cleanups**: fix OCR, normalize currencies, dates, tickers/ISINs; dedupe boilerplate; detect versions
- **PII/compliance**: redact PII if needed; attach `document_id`, `page`, `section`, `date` to every chunk for auditability

### 2. Indexing (small corpus, high precision)

- Create four lightweight indexes (no heavy infra needed for up to 100 docs):
  - **Semantic passages**: 512–800 token chunks, 15–20% overlap; keep parent heading and page
  - **Sparse/BM25**: keywords, regs, exact phrases
  - **Tables index**: each table as one unit + cell-level mini-chunks; store header → column types
  - **Entities index**: ISINs, tickers, fund names, people/roles, regulations; simple trie or SQLite table
- **Storage options** (all fine at this scale):
  - SQLite + FAISS (or LanceDB) for vectors
  - tantivy/Elasticsearch for BM25 (or on-disk Lucene via tantivy)

### 3. Retrieval pipeline (accurate, citation-first)

- **Query understanding**: detect intent (policy vs. performance vs. restriction); extract entities (ISIN, dates, currencies)
- **Query rewrite**: multi-query (2–3 paraphrases) or RAG-Fusion style fusion to widen recall
- **Hybrid retrieval**: top-k from each index → reciprocal rank fusion (RRF) → cross-encoder re-ranker (e.g., `bge-reranker-large`) to pick the most answerable passages/tables
- **Context builder**: group by document, prefer latest effective date; include page/section and table slices; cap context ~2–3k tokens
- **Citations**: always return [doc, page, section/table] with each claim

### 4. Table-aware answering (crucial in finance)

- Keep tables intact; pass them verbatim (CSV/Markdown) alongside the question
- For calculations (yields, CAGR, fee impact), call a code tool (Python) so the LLM delegates math instead of guessing
- For long tables, send header + matched rows/columns + 2–3 neighbors for context

### 5. Orchestration with a reasoning LLM

- **Tools**: `search_passages`, `search_tables`, `entity_lookup`, `math_python`, `date_math`, `units_fx`
- **Guardrails in the system prompt**:
  - "Use tools for math."
  - "Only answer from retrieved context; if missing, say you don’t know and ask to upload."
  - "Always attach citations with page numbers."
  - "Prefer the most recent effective date when sources conflict."

### 6. Prompting & output contract

- **System prompt**: compliance tone (not investment advice), citation policy, numerical accuracy rules
- **Structured JSON output**:

```json
{
  "answer_markdown": "...",
  "citations": [
    {
      "doc": "Prospectus_2024.pdf",
      "page": 47,
      "section": "Investment Restrictions"
    }
  ],
  "used_tables": [{ "doc": "Factsheet_Jun2025.pdf", "table_id": "T3" }],
  "calculations": [
    { "name": "OngoingFeeImpact", "inputs": { "...": "..." }, "result": 0.47 }
  ],
  "confidence": "high|medium|low"
}
```

- **Post-processor**: renders Markdown + collapsible “Sources” with deep links to page numbers

### 7. Minimal stack (fast, cheap, robust)

- **Ingestion**: Docling/Unstructured (PDF→MD/CSV/JSON), optional Mathpix for hard tables
- **Store**: S3/GCS for raw & normalized; SQLite + FAISS (or LanceDB) vectors; tantivy/Elasticsearch for BM25; SQLite table for entities
- **Orchestrator**: LangGraph/Colang-style graph or a small custom state machine
- **Observability**: Langfuse/OpenTelemetry; log prompts, tool calls, latency, and groundedness checks

### 8. Evaluation (before you ship)

- Build ~60 gold Q&A from your ~100 docs (policies, limits, fees, key dates, definitions, edge cases)
- **Metrics**:
  - Answer correctness (LLM judge with rubric)
  - Faithfulness (no claims outside context)
  - Citation accuracy
  - Table QA accuracy
  - Numeric error rate
  - Latency
  - Cost
- Create adversarial tests: ambiguous share classes, conflicting versions, footnotes vs main text, derived numbers (TER, fee caps)

### 9. Rollout & UX

- **Modes**: "Direct answer" and "Source-only" (just finds the best passages)
- **Answer style**: short executive summary → optional "Show working" (tables + math steps)
- **Follow-ups**: suggest clarifying filters (date range, share class, jurisdiction)
- **Safety**: never opine on securities; include a standard disclaimer

### 10. Build order (2-week plan for ~100 docs)

- Parsing & normalization with page anchors →
- Hybrid retrieval (BM25 + vectors) →
- Reranker →
- Citations & table passthrough →
- Python math tool →
- Evaluation set →
- Observability & guardrails

### “Good enough” baseline (day 1–2)

- Chunk to ~600 tokens with overlap; embed with a strong general embedding model
- BM25 via tantivy; FAISS for vectors; RRF + cross-encoder rerank
- Return top 6 passages + any matched tables; answer with citations
- Python tool for math/date; refuse outside-scope

### Upgrades that move the needle

- Entity-aware retrieval (ISIN/ticker normalization)
- Table retriever with column-type awareness
- Multi-query / HyDE for tougher questions
- Lightweight domain reranker fine-tune using ~200 labeled query↔passage pairs
- Versioning logic (prefer newest effective date; expose “as of” date in answers)
- Guarded reasoning: numeric cross-checks (sum to 100%, fee cap constraints, date sanity)
