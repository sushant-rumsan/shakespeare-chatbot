from dataclasses import dataclass
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from utils.config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K
from utils.llm import generate
from utils.prompts import build_baseline, build_explain, build_stylised

STYLISED_MAX_WORDS = 150


def enforce_word_limit(text, max_words=STYLISED_MAX_WORDS):
    """Keep stylised output within assignment limit."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " [...]"


@dataclass
class RetrievalResult:
    documents: list
    metadatas: list

    @property
    def context(self):
        return "\n\n".join(self.documents)


class RAGSystem:
    def __init__(self):
        if not Path(CHROMA_PATH).exists():
            raise FileNotFoundError(
                f"Chroma DB not found at {CHROMA_PATH}. Run: python ingest.py"
            )
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = client.get_collection(name=COLLECTION_NAME)

    def retrieve(self, question, play=None, top_k=TOP_K):
        query_embedding = self.embedding_model.encode(question).tolist()
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if play:
            kwargs["where"] = {"play": play}

        results = self.collection.query(**kwargs)
        return RetrievalResult(
            documents=results["documents"][0],
            metadatas=results["metadatas"][0],
        )

    # Static method as it doesn't need self object to be called
    @staticmethod
    def format_evidence(documents, metadatas, excerpt_len=800):
        parts = []
        for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
            header = (
                f"[{i}] {meta.get('play', '')} | Act {meta.get('act', '')} "
                f"Scene {meta.get('scene', '')} | {meta.get('scene_id', '')}"
            )
            speakers = meta.get("speakers", "")
            if speakers:
                header += f" | Speakers: {speakers}"
            excerpt = doc[:excerpt_len] + ("..." if len(doc) > excerpt_len else "")
            parts.append(f"{header}\n{excerpt}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def metadata_summary(metadatas):
        return "; ".join(
            f"{m.get('play', '')} Act {m.get('act', '')} Scene {m.get('scene', '')}"
            for m in metadatas
        )

    def answer_baseline(self, question):
        return generate(build_baseline(question))

    def answer_explain(self, question, play=None):
        retrieval = self.retrieve(question, play=play)
        answer = generate(build_explain(retrieval.context, question))
        evidence = self.format_evidence(
            retrieval.documents, retrieval.metadatas
        )
        meta_summary = self.metadata_summary(retrieval.metadatas)
        return evidence, meta_summary, answer

    def answer_stylised(self, question, play=None):
        retrieval = self.retrieve(question, play=play)
        answer = enforce_word_limit(
            generate(build_stylised(retrieval.context, question))
        )
        evidence = self.format_evidence(
            retrieval.documents, retrieval.metadatas
        )
        meta_summary = self.metadata_summary(retrieval.metadatas)
        return evidence, meta_summary, answer
