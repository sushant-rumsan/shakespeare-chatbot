# Shakespeare RAG (CSCI433/933 Assignment 2)

- This read me contains step by step guide to run the system.

## Setup

- Create virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Download ollama in mac:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

- Run llama3 model in background

```bash
ollama pull llama3
```

(By default, ollama runs in port: 11434, if this port is not available in your device, use different port.)

## Usage

- This reads the data, chunk it, create embeeding and store that in vector db
- Run this script first to get context in later steps

```bash
python ingest.py      # build chroma_db
```

- If you want individual query from the RAG, run this script
- Type your question in the CLI

```bash
python query.py
```

- Evaluate.py evaluates result of raw LLM and RAG multiple professor provided and student choosen question
- This creates 2 files, evaluate_results.json and evaluate_results.csv for ease of viewing result in 2 different format

```bash # interactive Q&A
python evaluate.py    # baseline vs RAG evaluation
```

## Evaluation outputs

- `evaluate_results.csv` — flat rows for manual scoring (responses + scene metadata; no full passages)
- `evaluate_results.json` — grouped by question, includes full `retrieved_passage` for grounding checks

## Analyze results

- Reads `evaluate_results.json` only (does not re-run the LLM).
- Writes `analyze_results.md` with flags and baseline vs RAG hints for your report.

```bash
python analyze_results.py
python analyze_results.py --stdout   # also print report to terminal
```
