from fastapi import FastAPI, Query
from llm.orchestrator import ask


app = FastAPI()


@app.get("/chat")
def chat(q: str = Query(...)):
    answer = ask(q)
    return {"query": q, "answer": answer}
