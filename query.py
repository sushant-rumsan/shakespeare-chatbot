from utils import RAGSystem

MODES = {
    "1": ("explain", "RAG explain — grounded answer with evidence"),
    "2": ("stylise", "RAG stylised — creative monologue (not factual)"),
    "3": ("baseline", "Baseline — no retrieval, general knowledge only"),
}


def prompt_play():
    play_input = input(
        "Filter by play (Hamlet / Macbeth / Romeo and Juliet)? [Enter=all plays]: "
    ).strip()
    return play_input or None


def run_mode(rag, mode, question, play):
    if mode == "baseline":
        print("\n--- Answer (baseline, no retrieved evidence) ---")
        print(rag.answer_baseline(question))
        return

    if mode == "stylise":
        evidence, meta_summary, answer = rag.answer_stylised(question, play=play)
        print("\n--- Retrieved evidence (inspiration only) ---")
        print(evidence)
        print(f"\n({meta_summary})")
        print("\n--- Stylised response (creative, not factual) ---")
        print(answer)
        print(f"\n({len(answer.split())} words)")
        return

    evidence, meta_summary, answer = rag.answer_explain(question, play=play)
    print("\n--- Retrieved evidence ---")
    print(evidence)
    print(f"\n({meta_summary})")
    print("\n--- Answer ---")
    print(answer)


def main():
    rag = RAGSystem()

    print("Shakespeare RAG")
    for key, (_, label) in MODES.items():
        print(f"  {key}. {label}")

    choice = input("\nMode [1=explain, 2=stylise, 3=baseline]: ").strip() or "1"
    mode = MODES.get(choice, MODES["1"])[0]

    question = input("Ask a question: ").strip()
    if not question:
        print("No question entered.")
        return

    play = prompt_play() if mode != "baseline" else None
    run_mode(rag, mode, question, play)


if __name__ == "__main__":
    main()
