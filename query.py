from utils import RAGSystem


def main():
    rag = RAGSystem()

    print("Shakespeare RAG (explain mode). Empty play = search all plays.")
    question = input("\nAsk a question: ").strip()
    if not question:
        print("No question entered.")
        return

    play_input = input(
        "Filter by play (Hamlet / Macbeth / Romeo and Juliet)? [Enter=skip]: "
    ).strip()
    play = play_input or None

    evidence, meta_summary, answer = rag.answer_explain(question, play=play)

    print("\n--- Retrieved evidence ---")
    print(evidence)
    print(f"\n({meta_summary})")
    print("\n--- Answer ---")
    print(answer)


if __name__ == "__main__":
    main()
