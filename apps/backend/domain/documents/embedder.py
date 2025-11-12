import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import textwrap

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def get_client(persist_dir: str = "/data/chroma"):
    # ✅ API baru
    return chromadb.PersistentClient(path=persist_dir)

def embed_texts(model: SentenceTransformer, texts: list[str]):
    return model.encode(texts, convert_to_numpy=True).tolist()

def store_embeddings(doc_id: str, text: str, persist_dir="/data/chroma"):
    client = get_client(persist_dir)
    collection = client.get_or_create_collection("documents")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunks = chunk_text(text)

    embeddings = embed_texts(model, chunks)
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"document_id": str(doc_id), "chunk_index": i} for i in range(len(chunks))]
    )

    return len(chunks)
