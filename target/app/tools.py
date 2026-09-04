from app.retrieval import retrieve, get_collection


def search_documents(query: str, top_k: int = 4):
    chunks = retrieve(query, top_k=top_k)
    return {
        "query": query,
        "results": [{"source": c["source"], "text": c["text"]} for c in chunks],
    }


def list_documents():
    collection = get_collection()
    data = collection.get()
    sources = sorted({meta.get("source", "unknown") for meta in data.get("metadatas", [])})
    return {"documents": sources}


def get_document_metadata(doc_id: str):
    collection = get_collection()
    data = collection.get(where={"doc_id": doc_id})
    chunk_count = len(data.get("ids", []))
    return {"doc_id": doc_id, "chunk_count": chunk_count, "found": chunk_count > 0}