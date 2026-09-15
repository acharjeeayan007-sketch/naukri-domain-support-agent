"""
rag/chunking.py - Two Chunking Strategies for Naukri.com Knowledge Base.
Track: Recruitment & HR (Naukri.com) - Capstone Part 1 Task 3.

Strategy A: Fixed-size chunks with overlap.
Strategy B: Sentence-based chunks with punctuation boundaries.
"""

import re
from typing import Any, Dict, List


def fixed_size_chunking(
    docs: List[Dict[str, Any]],
    chunk_size_chars: int = 180,
    overlap_chars: int = 40,
) -> List[Dict[str, Any]]:
    """
    Chunks document text into fixed character windows with sliding overlap.
    Maps each chunk back to its parent document ID.
    """
    chunks: List[Dict[str, Any]] = []

    for doc in docs:
        doc_id = doc["doc_id"]
        content = doc["content"]
        title = doc.get("title", "")
        topic = doc.get("topic", "")

        start = 0
        chunk_idx = 0
        doc_len = len(content)

        while start < doc_len:
            end = min(start + chunk_size_chars, doc_len)
            chunk_text = content[start:end].strip()

            if chunk_text:
                chunk_record = {
                    "chunk_id": f"{doc_id}-FIXED-{chunk_idx}",
                    "doc_id": doc_id,
                    "strategy": "fixed_size_overlap",
                    "chunk_index": chunk_idx,
                    "text": chunk_text,
                    "metadata": {
                        "doc_id": doc_id,
                        "title": title,
                        "topic": topic,
                        "start_char": start,
                        "end_char": end,
                        "strategy": "fixed_size_overlap",
                    },
                }
                chunks.append(chunk_record)
                chunk_idx += 1

            if end >= doc_len:
                break
            start += chunk_size_chars - overlap_chars

    return chunks


def sentence_based_chunking(
    docs: List[Dict[str, Any]],
    sentences_per_chunk: int = 1,
) -> List[Dict[str, Any]]:
    """
    Chunks document text by natural sentence boundaries.
    Preserves syntactic cohesion within each chunk.
    """
    chunks: List[Dict[str, Any]] = []

    for doc in docs:
        doc_id = doc["doc_id"]
        content = doc["content"]
        title = doc.get("title", "")
        topic = doc.get("topic", "")

        # Split on sentence terminals followed by space
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content) if s.strip()]

        for chunk_idx, sentence in enumerate(sentences):
            chunk_record = {
                "chunk_id": f"{doc_id}-SENT-{chunk_idx}",
                "doc_id": doc_id,
                "strategy": "sentence_based",
                "chunk_index": chunk_idx,
                "text": sentence,
                "metadata": {
                    "doc_id": doc_id,
                    "title": title,
                    "topic": topic,
                    "sentence_index": chunk_idx,
                    "strategy": "sentence_based",
                },
            }
            chunks.append(chunk_record)

    return chunks
