import requests
import chromadb

from sentence_transformers import SentenceTransformer

# -----------------------------------
# Load embedding model
# -----------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------------
# Connect to Chroma
# -----------------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="knowledge_base"
)

# -----------------------------------
# User query
# -----------------------------------

query = input("Ask a question: ")

# -----------------------------------
# Create query embedding
# -----------------------------------

query_embedding = embedding_model.encode(
    query
).tolist()

# -----------------------------------
# Retrieve similar chunks
# -----------------------------------

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

retrieved_docs = results["documents"][0]

context = "\n\n".join(retrieved_docs)

# -----------------------------------
# Prompt
# -----------------------------------

prompt = f"""
You are a careful assistant. Use ONLY the information in the Context section.
- If the Context is enough, give a concise answer in your own words.
- If the Context does not contain the answer, say: "I can't answer from the provided context.

Context:
{context}

Question:
{query}
"""

# -----------------------------------
# Call Ollama
# -----------------------------------

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
)

answer = response.json()["response"]

print("\nAnswer:\n")
print(answer)