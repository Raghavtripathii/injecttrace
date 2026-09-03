import os
import uuid

import chromadb

from app.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, SEED_DOCUMENTS_DIR


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        if end == length:
            break
        start = end - overlap

    return chunks


def load_seed_documents(directory=SEED_DOCUMENTS_DIR):
    documents = []

    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(directory, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        documents.append({"doc_id": filename, "source": filename, "content": content})

    return documents


def build_index(persist_dir=CHROMA_PERSIST_DIR, collection_name=COLLECTION_NAME):
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name=collection_name)

    documents = load_seed_documents()
    if not documents:
        raise RuntimeError(f"No .txt files found in {SEED_DOCUMENTS_DIR}")

    ids, texts, metadatas = [], [], []
    for doc in documents:
        for chunk in chunk_text(doc["content"]):
            ids.append(str(uuid.uuid4()))
            texts.append(chunk)
            metadatas.append({"source": doc["source"], "doc_id": doc["doc_id"]})

    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
    return len(texts)


if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} chunks from {SEED_DOCUMENTS_DIR}")