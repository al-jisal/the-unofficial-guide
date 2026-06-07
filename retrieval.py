"""Stage [3] Embedding + Vector Store, and Stage [4] Retrieval.

embed_store(chunks) -> embed each chunk with all-MiniLM-L6-v2 and store the
                       text + chunk_id in a persistent ChromaDB collection.
retrieve(query, n_results) -> embed the query and return the most relevant
                       chunks as {"text", "distance"} dicts (cosine distance,
                       lower = more similar).
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "course_selection"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Load the embedding model and Chroma client once at import time so repeated
# retrieve() calls don't reload the model.
_model = SentenceTransformer(EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=str(CHROMA_DIR))


def _get_collection():
    # cosine space so distances match the "lower = more similar" contract.
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def embed_store(chunks):
    """Embed each chunk with all-MiniLM-L6-v2 and store it in ChromaDB.

    `chunks` is a list of dicts with keys "text" and "chunk_id" (as produced
    by ingest.chunk_documents). Returns the number of chunks stored.
    """
    # Rebuild the collection from scratch so re-runs don't duplicate entries.
    if _has_collection():
        _client.delete_collection(COLLECTION_NAME)
    collection = _get_collection()

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    # chunk_id is "<filename>_<index>" — strip the index to recover the source
    # document so retrieval can surface it for citations.
    metadatas = [{"source": _source_from_id(cid)} for cid in ids]
    embeddings = _model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return collection.count()


def retrieve(query, n_results=5):
    """Retrieve the `n_results` most relevant chunks for `query`.

    Returns a list of dicts, each {"text", "source", "distance"}, ordered from
    most to least similar (cosine distance, lower = more similar). "source" is
    the document the chunk came from, for citation.
    """
    collection = _get_collection()
    query_embedding = _model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    return [
        {"text": text, "source": meta["source"], "distance": distance}
        for text, meta, distance in zip(documents, metadatas, distances)
    ]


def _source_from_id(chunk_id):
    # "reddit_thread_1.txt_5" -> "reddit_thread_1.txt"
    return chunk_id.rsplit("_", 1)[0]


def _has_collection():
    return COLLECTION_NAME in {c.name for c in _client.list_collections()}


if __name__ == "__main__":
    # Build the store from the documents, then run a sample query.
    from ingest import chunk_documents, load_documents

    all_chunks = []
    for doc in load_documents():
        all_chunks.extend(chunk_documents(doc["text"], doc["filename"]))

    count = embed_store(all_chunks)
    print(f"Stored {count} chunks in ChromaDB\n")

    sample_query = "Should I take four classes my first semester?"
    print(f"Query: {sample_query}\n")
    for i, hit in enumerate(retrieve(sample_query, n_results=3), 1):
        print(f"[{i}] distance={hit['distance']:.4f} source={hit['source']}")
        print(f"    {hit['text'][:160]}\n")
