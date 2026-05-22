"""
Structured evaluation: baseline vs RAG on instructor + group questions.
Outputs: evaluate_results.csv and evaluate_results.json
"""

import csv
import json
import time
from pathlib import Path

from utils import RAGSystem

OUTPUT_CSV = "evaluate_results.csv"
OUTPUT_JSON = "evaluate_results.json"
DATA_DIR = Path("./data")

# CSV omits full retrieved_passage (use evaluate_results.json for evidence text).
CSV_FIELDNAMES = [
    "question_id",
    "source",
    "play",
    "question",
    "expected_focus",
    "interaction",
    "system",
    "retrieved_metadata",
    "response",
    "correctness",
    "grounding",
    "retrieval_relevance",
    "usefulness",
    "style",
    "comments",
]


def row_for_csv(row):
    return {k: row[k] for k in CSV_FIELDNAMES}


def load_questions():
    questions = []
    for filename, source in (
        ("instructor_questions.json", "instructor"),
        ("group_questions.json", "group"),
    ):
        path = DATA_DIR / filename
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for q in data.get("questions", []):
            q = dict(q)
            q["source"] = source
            q.setdefault("interaction", "explain")
            questions.append(q)
    return questions


def make_row(q, system, interaction, evidence, meta_summary, answer, error=None):
    return {
        "question_id": q.get("id", ""),
        "source": q.get("source", ""),
        "play": q.get("play", ""),
        "question": q["question"],
        "expected_focus": q.get("expected_focus", ""),
        "interaction": interaction,
        "system": system,
        "retrieved_passage": evidence if not error else "",
        "retrieved_metadata": meta_summary if not error else "",
        "response": answer if not error else f"ERROR: {error}",
        "correctness": "",
        "grounding": "",
        "retrieval_relevance": "",
        "usefulness": "",
        "style": "",
        "comments": "",
    }


def evaluate_question(q, rag):
    rows = []
    question = q["question"]
    play = q.get("play") or None
    interaction = q.get("interaction", "explain")

    if interaction == "explain":
        runners = [
            ("baseline", lambda: ("", "", rag.answer_baseline(question))),
            (
                "rag",
                lambda: rag.answer_explain(question, play=play),
            ),
        ]
        for system, runner in runners:
            print(f"    {system}...")
            try:
                evidence, meta_summary, answer = runner()
                rows.append(
                    make_row(
                        q, system, "explain", evidence, meta_summary, answer
                    )
                )
            except Exception as e:
                rows.append(
                    make_row(q, system, "explain", "", "", "", error=e)
                )
            time.sleep(0.5)

    if interaction == "stylised":
        print("    rag (stylised)...")
        try:
            evidence, meta_summary, answer = rag.answer_stylised(
                question, play=play
            )
            rows.append(
                make_row(
                    q, "rag", "stylised", evidence, meta_summary, answer
                )
            )
        except Exception as e:
            rows.append(
                make_row(q, "rag", "stylised", "", "", "", error=e)
            )
        time.sleep(0.5)

    return rows


def group_results_by_question(rows):
    """Group flat rows by question_id for easier JSON reading."""
    questions = []
    index = {}

    for row in rows:
        qid = row["question_id"]
        if qid not in index:
            entry = {
                "question_id": qid,
                "source": row["source"],
                "play": row["play"],
                "question": row["question"],
                "expected_focus": row["expected_focus"],
                "runs": [],
            }
            index[qid] = entry
            questions.append(entry)

        index[qid]["runs"].append(
            {
                "interaction": row["interaction"],
                "system": row["system"],
                "retrieved_passage": row["retrieved_passage"],
                "retrieved_metadata": row["retrieved_metadata"],
                "response": row["response"],
                "correctness": row["correctness"],
                "grounding": row["grounding"],
                "retrieval_relevance": row["retrieval_relevance"],
                "usefulness": row["usefulness"],
                "style": row["style"],
                "comments": row["comments"],
            }
        )

    return questions


def main():
    questions = load_questions()
    if not questions:
        raise SystemExit("No questions found in data/")

    explain_count = sum(1 for q in questions if q.get("interaction") == "explain")
    stylised_count = sum(
        1 for q in questions if q.get("interaction") == "stylised"
    )
    print(f"Loaded {len(questions)} questions")
    print(f"  explain: {explain_count}  stylised: {stylised_count}")
    print("Ensure Ollama is running (ollama run llama3)\n")

    rag = RAGSystem()
    all_rows = []

    for q in questions:
        print(f"\n=== {q.get('id')} [{q.get('interaction')}] {q.get('play')}")
        print(f"    {q['question']}")
        all_rows.extend(evaluate_question(q, rag))

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(row_for_csv(row) for row in all_rows)

    grouped = group_results_by_question(all_rows)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(grouped, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Wrote {len(all_rows)} rows to {OUTPUT_CSV}")
    print(f"       Wrote {len(grouped)} questions to {OUTPUT_JSON}")
    print(
        "Next: score each row (1-5) for correctness, grounding, "
        "retrieval_relevance, usefulness, and style where applicable."
    )


if __name__ == "__main__":
    main()
