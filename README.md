# Shakespeare RAG Chatbot (CSCI433/933 Assignment 2)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install and run Ollama with Llama 3:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama run llama3
```

## Project layout

```
python_assignment/
├── data/                  # Play JSON + evaluation questions
├── utils/
│   ├── config.py          # Paths, model names
│   ├── llm.py             # Ollama API
│   ├── prompts.py         # Prompt templates
│   ├── rag.py             # RAGSystem (retrieve + generate)
│   └── chunking.py        # Scene-aware chunking
├── ingest.py              # Build vector index
├── query.py               # Interactive CLI
└── evaluate.py            # Batch evaluation → CSV
```

## Usage

```bash
# 1. Build the vector index (run after data changes)
python ingest.py

# 2. Interactive Q&A with retrieval + evidence
python query.py

# 3. Structured evaluation (baseline vs RAG) → evaluate_results.csv
python evaluate.py
```

## Evaluation

- **Instructor questions:** `data/instructor_questions.json` (6)
- **Group questions:** `data/group_questions.json` (7, includes 2 stylised)
- **Output:** `evaluate_results.csv` — fill scoring columns after manual review

Each explain question runs **baseline** (no retrieval) and **rag** (retrieval + generation).
Stylised questions run **rag** with a creative prompt (max 150 words, labelled as non-factual).
