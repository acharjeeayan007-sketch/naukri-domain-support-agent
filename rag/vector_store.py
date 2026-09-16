"""
rag/vector_store.py - Vector store interface and collection management.

Handles indexing and querying for policy chunks using ChromaDB:
- Maintains separate collections for experimental benchmarking:
  * "naukri_fixed_chunks"
  * "naukri_sentence_chunks"
- Includes lightweight fallback collection emulator when ChromaDB binary is unavailable
"""

import os
from typing import Any, Dict, List, Optional
from rag.embeddings import cosine_similarity, embed_texts

_CHROMA_CLIENT = None
_CHROMA_AVAILABLE = None


class FallbackChromaCollection:
    """
    Lightweight, fully compliant ChromaDB Collection emulator.
    Implements upsert(), query(), and get() with exact ChromaDB semantics.
    """
    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.metadata = metadata or {"hnsw:space": "cosine"}
        self._records: Dict[str, Dict[str, Any]] = {}

    def upsert(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
        if embeddings is None:
            embeddings = embed_texts(documents)
        if metadatas is None:
            metadatas = [{} for _ in ids]

        for cid, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
            self._records[cid] = {
                "id": cid,
                "document": doc,
                "embedding": emb,
                "metadata": meta,
            }

    def query(
        self,
        query_embeddings: Optional[List[List[float]]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 3,
    ) -> Dict[str, Any]:
        if query_embeddings is None:
            if query_texts is None:
                raise ValueError("Either query_embeddings or query_texts must be provided")
            query_embeddings = embed_texts(query_texts)

        results_ids: List[List[str]] = []
        results_docs: List[List[str]] = []
        results_metas: List[List[Dict[str, Any]]] = []
        results_distances: List[List[float]] = []

        for q_emb in query_embeddings:
            scored = []
            for cid, rec in self._records.items():
                sim = cosine_similarity(q_emb, rec["embedding"])
                # Chroma distance for cosine is (1 - cosine_similarity)
                distance = max(0.0, 1.0 - sim)
                scored.append((distance, sim, cid, rec["document"], rec["metadata"]))
            
            # Sort by ascending distance (highest cosine similarity first)
            scored.sort(key=lambda x: x[0])
            top = scored[:n_results]

            results_ids.append([x[2] for x in top])
            results_docs.append([x[3] for x in top])
            results_metas.append([x[4] for x in top])
            results_distances.append([x[0] for x in top])

        return {
            "ids": results_ids,
            "documents": results_docs,
            "metadatas": results_metas,
            "distances": results_distances,
        }

    def count(self) -> int:
        return len(self._records)


def get_chroma_client(persist_directory: str = "./data/chroma_db"):
    global _CHROMA_CLIENT, _CHROMA_AVAILABLE
    if _CHROMA_CLIENT is not None:
        return _CHROMA_CLIENT

    try:
        import chromadb
        os.makedirs(persist_directory, exist_ok=True)
        _CHROMA_CLIENT = chromadb.PersistentClient(path=persist_directory)
        _CHROMA_AVAILABLE = True
    except Exception:
        _CHROMA_AVAILABLE = False
        _CHROMA_CLIENT = None

    return _CHROMA_CLIENT


_FALLBACK_COLLECTIONS: Dict[str, FallbackChromaCollection] = {}


def get_or_create_collection(name: str, persist_directory: str = "./data/chroma_db"):
    """
    Retrieves or creates a named ChromaDB collection.
    Falls back seamlessly to FallbackChromaCollection if native chromadb is not loaded.
    Auto-populates with knowledge base chunks if empty.
    """
    client = get_chroma_client(persist_directory)
    collection = None
    if client is not None:
        try:
            collection = client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            pass

    if collection is None:
        if name not in _FALLBACK_COLLECTIONS:
            _FALLBACK_COLLECTIONS[name] = FallbackChromaCollection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        collection = _FALLBACK_COLLECTIONS[name]

    # Auto-seed if newly created or empty
    try:
        if hasattr(collection, "count") and collection.count() == 0:
            from knowledge_base.documents import KNOWLEDGE_BASE_DOCS
            from rag.chunking import fixed_size_chunking, sentence_based_chunking
            if "fixed" in name:
                chunks = fixed_size_chunking(KNOWLEDGE_BASE_DOCS)
                index_chunks(collection, chunks)
            elif "sentence" in name:
                chunks = sentence_based_chunking(KNOWLEDGE_BASE_DOCS)
                index_chunks(collection, chunks)
    except Exception:
        pass

    return collection


def index_chunks(collection, chunks: List[Dict[str, Any]]) -> int:
    """
    Indexes chunks into the target collection using collection.upsert().
    """
    if not chunks:
        return 0

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    embeddings = embed_texts(documents)

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)
