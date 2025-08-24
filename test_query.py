from llm.orchestrator import ask

if __name__ == "__main__":
    query = "What's the time to maturity of the fund?"
    answer = ask(query)
    print("Q:", query)
    print("A:", answer)
