from fastapi import FastAPI, Query
from dotenv import load_dotenv
from llm.orchestrator import ask

load_dotenv()


app = FastAPI()


@app.get("/chat")
def chat(q: str = Query(...)):
    answer = ask(q)
    return {"query": q, "answer": answer}
