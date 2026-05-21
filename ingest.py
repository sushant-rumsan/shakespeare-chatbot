import chromadb
from sentence_transformers import SentenceTransformer

from utils import chunks_from_play, load_play_files
from utils.config import COLLECTION_NAME, EMBEDDING_MODEL, CHROMA_PATH

BATCH_SIZE = 100

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=CHROMA_PATH)

try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.get_or_create_collection(name=COLLECTION_NAME)

plays = load_play_files("./data")
print(f"Loaded {len(plays)} play files")

all_chunks = []
for play in plays:
    play_title = play.get("metadata", {}).get("title", "Unknown")
    play_chunks = chunks_from_play(play)
    all_chunks.extend(play_chunks)
    print(f"  {play_title}: {len(play_chunks)} chunks")

print(f"Total chunks: {len(all_chunks)}")

for start in range(0, len(all_chunks), BATCH_SIZE):
    batch = all_chunks[start : start + BATCH_SIZE]

    texts = [chunk["text"] for chunk in batch]
    ids = [chunk["id"] for chunk in batch]
    metadatas = [chunk["metadata"] for chunk in batch]

    embeddings = embedding_model.encode(texts).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

print("Ingestion completed successfully!")
