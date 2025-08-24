from fastapi import FastAPI, Query, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm.orchestrator import ask, ask_with_context
from ingestion.parse_docs import parse_pdf
from ingestion.build_index import build_index
from retrieval.retriever import reload_indexes
from pathlib import Path
import json
from fastapi.staticfiles import StaticFiles

load_dotenv()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path("static/app")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/app", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/chat")
def chat(q: str = Query(...)):
    answer = ask(q)
    return {"query": q, "answer": answer}


@app.get("/chat_explain")
def chat_explain(q: str = Query(...)):
    result = ask_with_context(q)
    return {"query": q, **result}


@app.get("/pdf/{name}")
def get_pdf(name: str):
    path = Path("data/raw") / name
    if not path.exists():
        return {"ok": False, "message": "PDF not found"}
    return Response(content=path.read_bytes(), media_type="application/pdf")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def root_page():
    return """
    <!doctype html>
    <html>
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Financial RAG Bot</title>
      </head>
      <body>
        <div id=\"root\"></div>
        <script crossorigin src=\"https://unpkg.com/react@18/umd/react.production.min.js\"></script>
        <script crossorigin src=\"https://unpkg.com/react-dom@18/umd/react-dom.production.min.js\"></script>
        <script src=\"https://unpkg.com/@babel/standalone/babel.min.js\"></script>
        <script type=\"text/babel\" src=\"/static/app/main.js\"></script>
      </body>
    </html>
    """


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"ok": False, "message": "Only PDF files are supported"}

    raw_dir = Path("data/raw")
    processed_path = Path("data/processed/docs.jsonl")
    raw_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = raw_dir / file.filename

    # Save uploaded file
    contents = await file.read()
    pdf_path.write_bytes(contents)

    # Parse and append to processed jsonl
    sections = parse_pdf(pdf_path)
    with open(processed_path, "a") as f:
        for row in sections:
            f.write(json.dumps(row) + "\n")

    # Rebuild full index, then hot-reload in-memory structures
    build_index()
    reload_indexes()

    return {
        "ok": True,
        "message": f"Indexed {len(sections)} sections from {file.filename}",
    }
