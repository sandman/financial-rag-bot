from openai import OpenAI
from retrieval.retriever import hybrid_search
from load_dotenv import load_dotenv

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You are a financial research assistant. 
Answer only using provided context. 
Always cite [doc, page].
If context is missing, say "Not found in documents".
"""


def ask(query):
    hits = hybrid_search(query, top_k=6)
    context = ""
    for h in hits:
        doc, page, text = h[0]["doc"], h[0]["page"], h[0]["text"]
        context += f"[{doc} p.{page}]: {text}\n"

    prompt = f"{SYSTEM_PROMPT}\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"

    resp = client.chat.completions.create(
        model="gpt-4.1",  # or latest state-of-the-art reasoning model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content
