from llm.orchestrator import ask

if __name__ == "__main__":
    query = "What are the investment restrictions for this fund?"
    answer = ask(query)
    print("Q:", query)
    print("A:", answer)
