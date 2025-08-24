# llm/orchestrator.py
from openai import OpenAI
from retrieval.retriever import hybrid_search
from load_dotenv import load_dotenv

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You are a financial research assistant. 
Answer strictly using the provided context. 
Always cite the source as [doc, page].
If the answer is not in context, say "Not found in documents".
"""


def ask(query: str):
    hits = hybrid_search(query, top_k=6)

    # Build context string
    context = ""
    for h in hits:
        doc, page, text = h[0]["doc"], h[0]["page"], h[0]["text"]
        context += f"[{doc} p.{page}]: {text}\n"

    # Send to LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:",
        },
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1", messages=messages, temperature=0  # or gpt-4o-mini for cheaper
    )

    return resp.choices[0].message.content


def ask_with_context(query: str):
    hits = hybrid_search(query, top_k=6)

    context = ""
    for h in hits:
        doc, page, text = h[0]["doc"], h[0]["page"], h[0]["text"]
        context += f"[{doc} p.{page}]: {text}\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:",
        },
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1", messages=messages, temperature=0
    )

    return {
        "answer": resp.choices[0].message.content,
        "hits": [
            {
                "doc": h[0]["doc"],
                "page": h[0]["page"],
                "text": h[0]["text"],
                "score": h[1],
            }
            for h in hits
        ],
    }
