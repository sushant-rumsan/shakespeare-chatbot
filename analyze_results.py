"""
Read evaluate_results.json and print a comparison report for your write-up.

This does NOT replace manual scoring — it highlights patterns to help you
fill correctness / grounding / retrieval_relevance / usefulness / style
and write failure analysis in the report.

Usage:
  python analyze_results.py
  python analyze_results.py path/to/evaluate_results.json
"""

import json
import re
import sys
from pathlib import Path

DEFAULT_JSON = "evaluate_results.json"

META_PHRASES = re.compile(
    r"according to|based on|provided context|the passages|the text suggests",
    re.IGNORECASE,
)
UNKNOWN_PHRASES = re.compile(r"i don'?t know", re.IGNORECASE)


def load_results(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def word_count(text):
    return len(text.split())


def analyze_run(run):
    response = run.get("response", "")
    flags = []
    if run.get("response", "").startswith("ERROR:"):
        flags.append("ERROR")
    if META_PHRASES.search(response):
        flags.append("meta-phrasing")
    if UNKNOWN_PHRASES.search(response):
        flags.append("i-dont-know")
    if run.get("system") == "rag" and not run.get("retrieved_passage", "").strip():
        flags.append("no-evidence")
    if run.get("interaction") == "stylised":
        wc = word_count(response)
        if wc > 150:
            flags.append(f"over-150-words({wc})")
    return flags


def compare_pair(baseline_run, rag_run):
    """Simple automatic hints — you still assign 1-5 scores manually."""
    notes = []
    b_resp = baseline_run.get("response", "")
    r_resp = rag_run.get("response", "")

    if baseline_run.get("flags") and "ERROR" not in baseline_run["flags"]:
        pass
    if rag_run.get("flags"):
        notes.append(f"RAG flags: {', '.join(rag_run['flags'])}")

    if len(r_resp) > len(b_resp) * 1.5 and len(r_resp) > 80:
        notes.append("RAG answer much longer than baseline")
    if "i-dont-know" in rag_run.get("flags", []) and "i-dont-know" not in baseline_run.get(
        "flags", []
    ):
        notes.append("RAG refused but baseline did not — check retrieval")
    if "no-evidence" in rag_run.get("flags", []):
        notes.append("RAG had no retrieved passage")

    return notes


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON)
    if not path.exists():
        raise SystemExit(f"Not found: {path}. Run: python evaluate.py")

    data = load_results(path)
    explain_items = [q for q in data if any(r["interaction"] == "explain" for r in q["runs"])]
    stylised_items = [q for q in data if any(r["interaction"] == "stylised" for r in q["runs"])]

    print("=" * 60)
    print("EVALUATION ANALYSIS (for report / manual scoring)")
    print("=" * 60)
    print(f"Questions: {len(data)}  |  explain: {len(explain_items)}  |  stylised: {len(stylised_items)}")
    print()
    print("HOW TO USE THIS OUTPUT")
    print("- Flags are automatic hints, not final grades.")
    print("- Open evaluate_results.json for full passages and responses.")
    print("- Score each run 1-5 on: correctness, grounding, retrieval_relevance,")
    print("  usefulness, style (stylised only), and add comments for failures.")
    print()

    # Explain: baseline vs RAG
    print("-" * 60)
    print("EXPLAIN QUESTIONS (baseline vs RAG)")
    print("-" * 60)

    for item in explain_items:
        runs = {r["system"]: r for r in item["runs"] if r["interaction"] == "explain"}
        for r in runs.values():
            r["flags"] = analyze_run(r)

        print(f"\n[{item['question_id']}] {item['play']}: {item['question']}")
        print(f"  Expected focus: {item['expected_focus'][:100]}...")

        if "baseline" in runs:
            b = runs["baseline"]
            print(f"  BASELINE ({word_count(b['response'])} words): {b['response'][:120]}...")
            if b["flags"]:
                print(f"    flags: {b['flags']}")

        if "rag" in runs:
            r = runs["rag"]
            meta = r.get("retrieved_metadata", "") or "(none)"
            print(f"  RAG      ({word_count(r['response'])} words): {r['response'][:120]}...")
            print(f"    retrieved: {meta}")
            if r["flags"]:
                print(f"    flags: {r['flags']}")

        if "baseline" in runs and "rag" in runs:
            notes = compare_pair(runs["baseline"], runs["rag"])
            if notes:
                print(f"  Compare: {'; '.join(notes)}")

    # Stylised
    print("\n" + "-" * 60)
    print("STYLISED QUESTIONS (RAG only)")
    print("-" * 60)

    for item in stylised_items:
        for run in item["runs"]:
            if run["interaction"] != "stylised":
                continue
            run["flags"] = analyze_run(run)
            print(f"\n[{item['question_id']}] {item['play']}: {item['question']}")
            print(f"  Words: {word_count(run['response'])}")
            print(f"  Response: {run['response'][:200]}...")
            if run["flags"]:
                print(f"  flags: {run['flags']}")
            has_label = run["response"].strip().startswith(
                "[Creative stylised response"
            )
            print(f"  Has required label: {has_label}")

    # Summary counts
    all_runs = [r for q in data for r in q["runs"]]
    flag_counts = {}
    for r in all_runs:
        for f in analyze_run(r):
            flag_counts[f] = flag_counts.get(f, 0) + 1

    print("\n" + "=" * 60)
    print("FLAG SUMMARY (across all runs)")
    print("=" * 60)
    for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"  {flag}: {count}")
    print("\nDone. Use flagged items as starting points for failure analysis.")


if __name__ == "__main__":
    main()
