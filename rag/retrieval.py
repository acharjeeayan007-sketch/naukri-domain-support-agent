"""
rag/retrieval.py - Policy retrieval service with confidence-based fallback.

Executes vector similarity search against indexed HR policies:
- Computes cosine similarity of the query against indexed chunks
- Evaluates top match against a calibrated confidence cutoff (0.1800)
- Returns polite fallback message if the query is outside documented policies
"""

from typing import Any, Dict, List, Optional, Tuple
from rag.embeddings import embed_query
from rag.vector_store import get_or_create_collection

SIMILARITY_THRESHOLD = 0.1800
FALLBACK_ANSWER = (
    "I do not have sufficient information in the official Naukri.com recruitment and HR policy "
    "knowledge base to answer this query. Please contact the HR Operations Helpdesk or your "
    "assigned Talent Acquisition representative."
)


def retrieve_context(
    query: str,
    collection_name: str = "naukri_sentence_chunks",
    top_k: int = 3,
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Retrieves the top-k chunks from the specified vector collection.
    Returns (retrieved_chunks, top_1_similarity).
    """
    collection = get_or_create_collection(collection_name)
    q_emb = embed_query(query)
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)

    chunks: List[Dict[str, Any]] = []
    top_1_sim = 0.0

    if results and results.get("ids") and results["ids"][0]:
        num_res = len(results["ids"][0])
        for i in range(num_res):
            dist = results["distances"][0][i]
            sim = max(0.0, 1.0 - dist)
            if i == 0:
                top_1_sim = sim

            chunk_info = {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": round(sim, 4),
                "distance": round(dist, 4),
            }
            chunks.append(chunk_info)

    return chunks, top_1_sim


def generate_grounded_answer(
    query: str,
    collection_name: str = "naukri_sentence_chunks",
    top_k: int = 3,
    threshold: float = SIMILARITY_THRESHOLD,
) -> Dict[str, Any]:
    """
    Generates a deterministic grounded response based strictly on retrieved context.
    If top similarity is below the calibrated threshold, returns the standard fallback.
    """
    chunks, top_sim = retrieve_context(query, collection_name=collection_name, top_k=top_k)

    if top_sim < threshold or not chunks:
        return {
            "query": query,
            "is_grounded": False,
            "fallback_triggered": True,
            "top_similarity": round(top_sim, 4),
            "threshold": threshold,
            "answer": FALLBACK_ANSWER,
            "retrieved_chunks": chunks,
            "primary_doc_id": None,
            "collection_used": collection_name,
        }

    # Synthesize grounded answer strictly from top chunk texts
    primary_doc_id = chunks[0]["metadata"].get("doc_id", "UNKNOWN")
    primary_topic = chunks[0]["metadata"].get("topic", "Policy")
    primary_title = chunks[0]["metadata"].get("title", "Policy Document")

    # Compose grounded answer
    context_sentences = [c["text"].strip() for c in chunks]
    unique_sentences = []
    for s in context_sentences:
        if s not in unique_sentences:
            unique_sentences.append(s)

    grounded_body = " ".join(unique_sentences[:3])
    final_answer = (
        f"According to Naukri.com's official {primary_title} ({primary_doc_id}): {grounded_body}"
    )

    return {
        "query": query,
        "is_grounded": True,
        "fallback_triggered": False,
        "top_similarity": round(top_sim, 4),
        "threshold": threshold,
        "answer": final_answer,
        "retrieved_chunks": chunks,
        "primary_doc_id": primary_doc_id,
        "primary_topic": primary_topic,
        "collection_used": collection_name,
    }
