import chromadb

from app.config import CHROMA_PERSIST_DIR, COLLECTION_NAME


def get_collection(persist_dir=CHROMA_PERSIST_DIR, collection_name=COLLECTION_NAME):
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(name=collection_name)


def retrieve(query, top_k=4):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    chunks = []
    for text, meta in zip(documents, metadatas):
        chunks.append({"text": text, "source": meta.get("source", "unknown")})

    return chunks