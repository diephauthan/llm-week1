from agent import run_agent

def main():
    print("cnc assistant v0. gõ q để thoát")
    while True:
        question = input("\nbạn: ").strip()
        if question.lower() in ("q", "quit", "exit"):
            break
        if not question:
            continue
        answer = run_agent(question)
        print("trợ lí:", answer)

if __name__ == "__main__":
    main()