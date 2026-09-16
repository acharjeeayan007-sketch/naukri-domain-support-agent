"""
tools/status_lookup_tool.py - Candidate application resolver and queue prioritization.

Queries candidate records and calculates urgency for recruiter intervention:
- Prioritization formula balances fast-track candidate flags with days spent pending in pipeline:
    score = (0.60 * priority_flag) + (0.40 * (days_pending / 30.0))
- Calibrated 80th-percentile threshold (0.6400) triggers expedited recruiter review
"""

from typing import Any, Dict, Optional
from dataset import JOB_APPLICATIONS_BY_ID

# Target top quintile (80th percentile) for recruiter escalation
ESCALATION_THRESHOLD = 0.6400


def calculate_escalation_score(days_since_created: int, flagged_priority_review: bool) -> float:
    """Computes the weighted composite escalation score in [0.0, 1.0]."""
    recency_signal = min(30, max(0, days_since_created)) / 30.0
    priority_signal = 1.0 if flagged_priority_review else 0.0
    return round(0.60 * priority_signal + 0.40 * recency_signal, 4)


def check_job_application_status(record_id: str) -> Dict[str, Any]:
    """
    Looks up a candidate job application by record_id and computes its escalation score.
    Returns status, expected_salary_inr, and detailed escalation diagnostics.
    """
    cleaned_id = record_id.strip().upper()
    record = JOB_APPLICATIONS_BY_ID.get(cleaned_id)

    if not record:
        return {
            "found": False,
            "record_id": cleaned_id,
            "error": f"Application record '{cleaned_id}' not found in recruitment database.",
            "status": None,
            "expected_salary_inr": None,
            "escalation_score": None,
            "escalation_recommended": False,
        }

    days = record["days_since_created"]
    flagged = record["flagged_priority_review"]
    score = calculate_escalation_score(days, flagged)
    escalate = score >= ESCALATION_THRESHOLD

    rationale = (
        f"Score {score:.4f} exceeds 80th percentile threshold ({ESCALATION_THRESHOLD}) "
        f"[Flagged: {flagged}, Days pending: {days}/30]"
        if escalate
        else f"Score {score:.4f} is within normal operational tolerances (< {ESCALATION_THRESHOLD}) "
        f"[Flagged: {flagged}, Days pending: {days}/30]"
    )

    return {
        "found": True,
        "record_id": cleaned_id,
        "category": record["category"],
        "status": record["status"],
        "expected_salary_inr": record["expected_salary_inr"],
        "days_since_created": days,
        "flagged_priority_review": flagged,
        "escalation_score": score,
        "escalation_threshold": ESCALATION_THRESHOLD,
        "escalation_recommended": escalate,
        "rationale": rationale,
    }


if __name__ == "__main__":
    # Demonstrate on a normal record and a high-escalation record
    print("Normal Record:")
    print(check_job_application_status("APP-1001"))
    
    # Find a record with escalation_recommended=True
    for r in JOB_APPLICATIONS_BY_ID.values():
        res = check_job_application_status(r["record_id"])
        if res["escalation_recommended"]:
            print("\nEscalated Record:")
            print(res)
            break
