import argparse
import json
import re
from pathlib import Path

DEFAULT_JSON = "evaluate_results.json"
DEFAULT_MD = "analyze_results.md"

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
    notes = []
    b_resp = baseline_run.get("response", "")
    r_resp = rag_run.get("response", "")

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


class MarkdownReport:
    def __init__(self, stdout: bool = False):
        self._lines: list[str] = []
        self._stdout = stdout

    def line(self, text: str = "") -> None:
        self._lines.append(text)
        if self._stdout:
            print(text)

    def text(self) -> str:
        return "\n".join(self._lines) + "\n"

    def write(self, path: Path) -> None:
        path.write_text(self.text(), encoding="utf-8")


def build_report(data: list, source: Path) -> MarkdownReport:
    explain_items = [q for q in data if any(r["interaction"] == "explain" for r in q["runs"])]
    stylised_items = [q for q in data if any(r["interaction"] == "stylised" for r in q["runs"])]

    report = MarkdownReport()
    report.line("# Evaluation analysis")
    report.line()
    report.line(f"Source: `{source}`")
    report.line()
    report.line(
        f"**Questions:** {len(data)} | **explain:** {len(explain_items)} | "
        f"**stylised:** {len(stylised_items)}"
    )
    report.line()
    report.line("## How to use this report")
    report.line()
    report.line("- Flags are automatic hints, not final grades.")
    report.line("- Open `evaluate_results.json` for full passages and responses.")
    report.line(
        "- Score each run 1–5 on: correctness, grounding, retrieval_relevance, "
        "usefulness, style (stylised only), and add comments for failures."
    )
    report.line()
    report.line("## Explain questions (baseline vs RAG)")
    report.line()

    for item in explain_items:
        runs = {r["system"]: r for r in item["runs"] if r["interaction"] == "explain"}
        for r in runs.values():
            r["flags"] = analyze_run(r)

        report.line(f"### [{item['question_id']}] {item['play']}")
        report.line()
        report.line(f"**Question:** {item['question']}")
        focus = item["expected_focus"]
        if len(focus) > 100:
            focus = focus[:100] + "..."
        report.line(f"**Expected focus:** {focus}")
        report.line()

        if "baseline" in runs:
            b = runs["baseline"]
            preview = b["response"][:120].replace("\n", " ")
            if len(b["response"]) > 120:
                preview += "..."
            report.line(f"- **Baseline** ({word_count(b['response'])} words): {preview}")
            if b["flags"]:
                report.line(f"  - flags: `{', '.join(b['flags'])}`")

        if "rag" in runs:
            r = runs["rag"]
            preview = r["response"][:120].replace("\n", " ")
            if len(r["response"]) > 120:
                preview += "..."
            meta = r.get("retrieved_metadata", "") or "(none)"
            report.line(f"- **RAG** ({word_count(r['response'])} words): {preview}")
            report.line(f"  - retrieved: {meta}")
            if r["flags"]:
                report.line(f"  - flags: `{', '.join(r['flags'])}`")

        if "baseline" in runs and "rag" in runs:
            notes = compare_pair(runs["baseline"], runs["rag"])
            if notes:
                report.line(f"- **Compare:** {'; '.join(notes)}")

        report.line()

    report.line("## Stylised questions (RAG only)")
    report.line()

    for item in stylised_items:
        for run in item["runs"]:
            if run["interaction"] != "stylised":
                continue
            run["flags"] = analyze_run(run)
            report.line(f"### [{item['question_id']}] {item['play']}")
            report.line()
            report.line(f"**Question:** {item['question']}")
            preview = run["response"][:200].replace("\n", " ")
            if len(run["response"]) > 200:
                preview += "..."
            report.line(f"- **Words:** {word_count(run['response'])}")
            report.line(f"- **Response:** {preview}")
            if run["flags"]:
                report.line(f"- **flags:** `{', '.join(run['flags'])}`")
            has_label = run["response"].strip().startswith("[Creative stylised response")
            report.line(f"- **Has required label:** {has_label}")
            report.line()

    all_runs = [r for q in data for r in q["runs"]]
    flag_counts: dict[str, int] = {}
    for r in all_runs:
        for f in analyze_run(r):
            flag_counts[f] = flag_counts.get(f, 0) + 1

    report.line("## Flag summary (across all runs)")
    report.line()
    for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        report.line(f"- `{flag}`: {count}")
    report.line()
    report.line(
        "*Use flagged items as starting points for failure analysis in your technical report.*"
    )

    return report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze evaluate_results.json and write analyze_results.md"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_JSON,
        help=f"Path to evaluation JSON (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_MD,
        help=f"Markdown output path (default: {DEFAULT_MD})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print the report to the terminal",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f"Not found: {path}. Run: python evaluate.py")

    data = load_results(path)
    report = build_report(data, path)
    out_path = Path(args.output)
    report.write(out_path)

    print(f"Wrote {out_path} (source: {path})")
    if args.stdout:
        print()
        print(report.text(), end="")


if __name__ == "__main__":
    main()
