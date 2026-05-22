# Shakespeare RAG (CSCI433/933 Assignment 2)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ollama pull llama3
```

## Usage

```bash
python ingest.py      # build chroma_db
python query.py       # interactive Q&A
python evaluate.py    # baseline vs RAG evaluation
```

## Evaluation outputs

- `evaluate_results.csv` — flat rows (spreadsheet / scoring)
- `evaluate_results.json` — grouped by question (easier to read in editor)
