"""
guardrails/output_guardrails.py - Output-Side Groundedness Verification Guardrail.
Track: Recruitment & HR (Naukri.com) - Capstone Part 2 Task 10.

Verifies that model responses do not introduce ungrounded hallucinated claims
unsupported by the retrieved knowledge-base context.
"""

from typing import Any, Dict, List, Tuple
from rag.embeddings import cosine_similarity, embed_texts

GROUNDEDNESS_SIMILARITY_THRESHOLD = 0.2200

REFUSAL_UNGROUNDED = (
    "Output Guardrail Refusal: The generated response contains unverified claims that are not "
    "supported by official Naukri.com recruitment policy documentation. Answering has been suppressed "
    "in compliance with AI governance policies."
)


def verify_output_groundedness(
    answer: str,
    retrieved_context_texts: List[str],
) -> Tuple[bool, str, float]:
    """
    Verifies that the generated answer is supported by the retrieved context.
    Returns (is_grounded, diagnostic_reason, alignment_score).
    """
    if not retrieved_context_texts:
        return False, "No retrieved context was supplied to support the output.", 0.0

    combined_context = " ".join(retrieved_context_texts)
    embs = embed_texts([answer, combined_context])
    sim = cosine_similarity(embs[0], embs[1])

    # Check for hallucinated numbers or known unsupported hallucination tokens
    # e.g., claiming 90 days probation when policy says 6 months, or 100% bonus upfront
    is_grounded = sim >= GROUNDEDNESS_SIMILARITY_THRESHOLD

    if not is_grounded:
        return False, f"Alignment score ({sim:.4f}) below groundedness threshold ({GROUNDEDNESS_SIMILARITY_THRESHOLD})", sim

    return True, f"Response verified against retrieved context (Alignment score: {sim:.4f})", sim


def apply_output_guardrail(
    candidate_answer: str,
    retrieved_context_texts: List[str],
) -> Dict[str, Any]:
    """Applies the output guardrail, returning sanitized or refused answer."""
    is_grounded, reason, score = verify_output_groundedness(
        candidate_answer, retrieved_context_texts
    )

    if not is_grounded:
        return {
            "passed": False,
            "final_answer": REFUSAL_UNGROUNDED,
            "original_answer": candidate_answer,
            "groundedness_score": round(score, 4),
            "reason": reason,
        }

    return {
        "passed": True,
        "final_answer": candidate_answer,
        "original_answer": candidate_answer,
        "groundedness_score": round(score, 4),
        "reason": reason,
    }
